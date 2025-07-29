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
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)    # Line numbers

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

    while True:
        stdscr.clear()
        # Title bar
        if curses.has_colors():
            stdscr.addstr(0, 0, f" Tini Editor - {filename} - Ctrl+S to save, Ctrl+Q to quit ", curses.color_pair(1) | curses.A_BOLD)
        else:
            stdscr.addstr(0, 0, f" Tini Editor - {filename} - Ctrl+S to save, Ctrl+Q to quit ")

        # Display each line with a light gray line number
        for i, line in enumerate(text):
            line_number = f"{i+1:>4} "
            if curses.has_colors():
                stdscr.addstr(i+1, 0, line_number, curses.color_pair(2))
                stdscr.addstr(i+1, 5, line)
            else:
                stdscr.addstr(i+1, 0, line_number + line)

        # Move the cursor to the current position (y+1 because of the title, x+5 for line numbers)
        stdscr.move(y+1, x+5)

        key = stdscr.getch()

        if key == 17:  # Ctrl+Q
            break
        elif key == 19:  # Ctrl+S
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(text))
        elif key == 10:  # Enter
            text.insert(y+1, "")
            y += 1
            x = 0
        elif key in (curses.KEY_BACKSPACE, 127, 8):
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
        elif key == curses.KEY_DOWN:
            if y < len(text) - 1:
                y += 1
                x = min(x, len(text[y]))
        elif key == curses.KEY_LEFT:
            if x > 0:
                x -= 1
            elif y > 0:
                y -= 1
                x = len(text[y])
        elif key == curses.KEY_RIGHT:
            if x < len(text[y]):
                x += 1
            elif y < len(text) - 1:
                y += 1
                x = 0
        elif 32 <= key <= 126:
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

curses.wrapper(main)
