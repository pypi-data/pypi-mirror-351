import sys
import curses
import os

def main(stdscr):
    curses.curs_set(1)
    stdscr.clear()

    # Enable color if possible and define color pairs
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Title bar
        # Use COLOR_WHITE for light gray if available, or COLOR_CYAN as fallback
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Line numbers

    if len(sys.argv) < 2:
        stdscr.addstr(0, 0, "Usage: tini <filename>")
        stdscr.refresh()
        stdscr.getch()
        return

    filename = sys.argv[1]

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read().splitlines()
    else:
        text = [""]

    y = len(text) - 1 if text else 0
    x = len(text[y]) if text else 0

    undo_stack = []  # Stack to store previous states for undo
    redo_stack = []  # Stack to store states for redo

    scroll_y = 0  # Topmost visible line
    scroll_x = 0  # Leftmost visible column

    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        text_height = max_y - 1  # Leave room for title

        # Adjust scroll_y to keep cursor in view vertically
        if y - scroll_y >= text_height:
            scroll_y = y - text_height + 1
        elif y < scroll_y:
            scroll_y = y

        # Adjust scroll_x to keep cursor in view horizontally
        if x - scroll_x >= max_x - 5:  # 5 for line number width
            scroll_x = x - (max_x - 5) + 1
        elif x < scroll_x:
            scroll_x = x

        # Title bar
        if curses.has_colors():
            stdscr.addstr(0, 0, f" Tini Editor - {filename} - Ctrl+S to save, Ctrl+Q to quit ", curses.color_pair(1) | curses.A_BOLD)
        else:
            stdscr.addstr(0, 0, f" Tini Editor - {filename} - Ctrl+S to save, Ctrl+Q to quit ")

        # Display visible lines with line numbers
        for i in range(scroll_y, min(len(text), scroll_y + text_height)):
            line_number = f"{i+1:>4} "
            if curses.has_colors():
                stdscr.addstr(i - scroll_y + 1, 0, line_number, curses.color_pair(2))
                stdscr.addstr(i - scroll_y + 1, 5, text[i][scroll_x:scroll_x + max_x - 5])
            else:
                stdscr.addstr(i - scroll_y + 1, 0, line_number + text[i][scroll_x:scroll_x + max_x - 5])

        # Move the cursor to the current position (adjusted for scroll)
        stdscr.move(y - scroll_y + 1, x - scroll_x + 5)

        key = stdscr.getch()

        if key == 17:  # Ctrl+Q
            # Check if file has been modified before exiting
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    original = f.read().splitlines()
            except FileNotFoundError:
                original = [""]
            if text != original:
                # Prompt user to save changes
                stdscr.addstr(len(text)+2, 0, "File modified. Save before exit? (y/n): ")
                stdscr.refresh()
                while True:
                    yn = stdscr.getch()
                    if yn in (ord('y'), ord('Y')):
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write("\n".join(text))
                        break
                    elif yn in (ord('n'), ord('N')):
                        break
                # Clear undo and redo history on exit
                undo_stack.clear()
                redo_stack.clear()
                break
            else:
                break
        elif key == 19:  # Ctrl+S
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(text))
            undo_stack.clear()  # Clear undo history on save
            redo_stack.clear()  # Clear redo history on save
        elif key == 26:  # Ctrl+Z for undo
            if undo_stack:
                redo_stack.append((text.copy(), y, x))  # Save current state for redo
                prev_text, prev_y, prev_x = undo_stack.pop()
                text = prev_text
                y = prev_y
                x = prev_x
        elif key == 25:  # Ctrl+Y for redo
            if redo_stack:
                undo_stack.append((text.copy(), y, x))  # Save current state for undo
                next_text, next_y, next_x = redo_stack.pop()
                text = next_text
                y = next_y
                x = next_x
        elif key == 10:  # Enter
            undo_stack.append((text.copy(), y, x))
            redo_stack.clear()  # Clear redo history on new edit
            text.insert(y+1, "")
            y += 1
            x = 0
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            undo_stack.append((text.copy(), y, x))
            redo_stack.clear()  # Clear redo history on new edit
            if x > 0:
                text[y] = text[y][:x-1] + text[y][x:]
                x -= 1
            elif y > 0:
                x = len(text[y-1])
                text[y-1] += text[y]
                del text[y]
                y -= 1
        elif key == curses.KEY_UP:
            if y > 0:
                y -= 1
                x = min(x, len(text[y]))
            # Prevent negative y and x
            if y < 0:
                y = 0
            if x < 0:
                x = 0
        elif key == curses.KEY_DOWN:
            if y < len(text) - 1:
                y += 1
                x = min(x, len(text[y]))
            # Prevent y from exceeding bounds
            if y < 0:
                y = 0
            if y >= len(text):
                y = len(text) - 1
            if x < 0:
                x = 0
        elif key == curses.KEY_LEFT:
            if x > 0:
                x -= 1
            elif y > 0:
                y -= 1
                x = len(text[y])
            # Prevent negative x and y
            if x < 0:
                x = 0
            if y < 0:
                y = 0
        elif key == curses.KEY_RIGHT:
            if x < len(text[y]):
                x += 1
            elif y < len(text) - 1:
                y += 1
                x = 0
            # Prevent x and y from exceeding bounds
            if x < 0:
                x = 0
            if y < 0:
                y = 0
            if y >= len(text):
                y = len(text) - 1
        elif 32 <= key <= 126:
            undo_stack.append((text.copy(), y, x))
            redo_stack.clear()  # Clear redo history on new edit
            # Ensure y is valid and text is not empty
            if y < 0:
                y = 0
            if not text:
                text.append("")
            if y >= len(text):
                text.append("")
                y = len(text) - 1
            # Insert character at cursor
            text[y] = text[y][:x] + chr(key) + text[y][x:]
            x += 1
        elif key == 9: # check for Tab key and add 4 spaces
            undo_stack.append((text.copy(), y, x))
            if y < 0:
                y = 0
            if not text:
                text.append("")
            if y >= len(text):
                text.append("")
                y = len(text) - 1
            text[y] = text[y][:x] + "    " + text[y][x:]
            x += 4
            redo_stack.clear()

def run():
    import curses
    curses.wrapper(main)
