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
        Binding("ctrl+q", "quit", "Quit"),
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
        with open(self.filename, "w") as f:
            f.write(self.text_area.text)  # Use .text instead of .value
        self.bell()  # give feedback

    def action_quit(self):
        self.exit()

def main():
    if len(sys.argv) < 2:
        print("Usage: tini <filename>")
        sys.exit(1)
    filename = sys.argv[1]
    app = NanoEditor(filename)
    app.run()
