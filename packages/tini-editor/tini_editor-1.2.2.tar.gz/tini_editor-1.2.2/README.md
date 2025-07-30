# tini-editor 📝

**tini** is a minimal, terminal-based text editor built with Python's [curses](https://docs.python.org/3/library/curses.html) module. It's inspired by `nano`, but written in Python and designed for simplicity and speed.

## ✨ Features

- Open and edit any text file from the terminal
- Keyboard shortcuts:
  - `Ctrl+S` – Save
  - `Ctrl+Q` – Quit (prompts to save if file is modified)
  - `Ctrl+Z` – Undo
  - `Ctrl+Y` – Redo
  - `Enter` – New line
  - `Backspace` – Delete character to the left
  - `Delete` – Delete character to the right
  - `Arrow keys` – Move cursor
- Line numbers
- Undo/Redo history (cleared on save or exit)
- Automatic scrolling for both vertical and horizontal movement
- If the file doesn’t exist, it will be created when saved

---

## 🚀 Installation

```bash
pip install tini-editor
```

---

## 🧑‍💻 Usage

```bash
tini <filename>
```

Example:

```bash
tini notes.txt
```

---

## 📦 Development Setup

Clone the repo and install dependencies:

```bash
git clone https://codeberg.org/yourusername/tini-editor.git
cd tini-editor
pip install -e .
```

Run locally:

```bash
python -m tini.app <filename>
```

---

## 🗺️ Planned Features

- Syntax highlighting for popular languages
- Copy, cut, and paste support
- Text selection and highlighting
- Search and replace
- Configurable tab width and indentation
- Mouse support (where available)
- Customizable color themes
- Status bar with file info and cursor position

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

* Built with [curses](https://docs.python.org/3/library/curses.html)
* Inspired by `nano`, but even tinier
