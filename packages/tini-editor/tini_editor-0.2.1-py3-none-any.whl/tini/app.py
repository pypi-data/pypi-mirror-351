import sys
import curses
import os
from colorist import BrightColor

def main(stdscr):
    curses.curs_set(1)
    stdscr.clear()
    # Get filename from command line
    if len(sys.argv) < 2:
        stdscr.addstr(0, 0, "Usage: tini <filename>")
        stdscr.refresh()
        stdscr.getch()
        return
    filename = sys.argv[1]
    # Load file if it exists
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read().splitlines()
    else:
        text = [""]
    y = len(text) - 1 if text else 0
    x = len(text[y]) if text else 0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"{BrightColor.MAGENTA} Tini Editor - {filename} - Ctrl+S to save, Ctrl+Q to quit {BrightColor.OFF}")
        for i, line in enumerate(text):
            stdscr.addstr(i+1, 0, line)
        stdscr.move(y+1, x)
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
            text[y] = text[y][:x] + chr(key) + text[y][x:]
            x += 1
        # else: ignore other keys

curses.wrapper(main)
