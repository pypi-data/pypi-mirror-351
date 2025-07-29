# tini.py
import sys
import os

from textual.app import App, ComposeResult
from textual.widgets import Input, Footer, Header, TextArea
from textual.reactive import reactive
from textual.binding import Binding

class NanoEditor(App):
    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+x", "quit", "Quit"),
        Binding("ctrl+f", "search", "Search"),
        Binding("ctrl+r", "search_and_replace", "Search and Replace"),
        Binding("ctrl+g", "goto", "Go to Line"),
        Binding("ctrl+z", "undo", "Undo"),
        Binding("ctrl+y", "redo", "Redo"),
    ]

    def __init__(self, filename, **kwargs):
        super().__init__(**kwargs)
        self.filename = filename
        self.text_area = TextArea()
        self.content = ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.text_area
        yield Footer()

    def on_mount(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                self.content = f.read()
        self.text_area.value = self.content

    def action_save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(self.text_area.text)
        self.bell()  # give feedback

    def action_search(self):
        search_term = self.text_area.prompt("Search: ")
        if search_term:
            index = self.text_area.value.find(search_term)
            if index != -1:
                self.text_area.cursor_position = index
                self.text_area.scroll_to_cursor()
            else:
                self.text_area.prompt("Not found", timeout=2)

    def action_search_and_replace(self):
        search_term = self.text_area.prompt("Search: ")
        if search_term:
            replace_term = self.text_area.prompt("Replace with: ")
            self.text_area.value = self.text_area.value.replace(search_term, replace_term)
            self.text_area.refresh()
            index = self.text_area.value.find(search_term)
            if index != -1:
                self.text_area.cursor_position = index
                self.text_area.scroll_to_cursor()
            else:
                self.text_area.prompt("Not found", timeout=2)
    
    def action_goto(self):
        line_number = self.text_area.prompt("Go to line: ")
        try:
            line_number = int(line_number) - 1  # Convert to zero-based index
            lines = self.text_area.value.splitlines()
            if 0 <= line_number < len(lines):
                self.text_area.cursor_position = self.text_area.value.index(lines[line_number])
                self.text_area.scroll_to_cursor()
            else:
                self.text_area.prompt("Line number out of range", timeout=2)
        except ValueError:
            self.text_area.prompt("Invalid line number", timeout=2)

    def action_undo(self):
        if self.text_area.can_undo:
            self.text_area.undo()
        else:
            self.text_area.prompt("Nothing to undo", timeout=2)
    
    def action_redo(self):
        if self.text_area.can_redo:
            self.text_area.redo()
        else:
            self.text_area.prompt("Nothing to redo", timeout=2)
            
    def action_quit(self):
        self.exit()

def main():
    if len(sys.argv) < 2:
        print("Usage: tini <filename>")
        sys.exit(1)
    filename = sys.argv[1]
    app = NanoEditor(filename)
    app.run()
