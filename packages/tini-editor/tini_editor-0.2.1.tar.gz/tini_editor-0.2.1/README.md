# tini-editor 📝

**tini** is a minimal, terminal-based text editor built with Python's [curses](https://docs.python.org/3/library/curses.html) module. It's inspired by `nano`, but written in Python and designed for simplicity and speed.

## ✨ Features

- Open and edit any text file from the terminal
- Keyboard shortcuts:
  - `Ctrl+S` – Save
  - `Ctrl+Q` – Quit
- Built with the standard Python [curses](https://docs.python.org/3/library/curses.html) TUI framework

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

If the file doesn’t exist, it will be created when saved.

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

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

* Built with [curses](https://docs.python.org/3/library/curses.html)
* Inspired by `nano`, but even tinier
