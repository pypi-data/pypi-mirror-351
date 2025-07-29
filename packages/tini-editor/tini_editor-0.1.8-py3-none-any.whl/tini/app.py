# tini.py
import sys
import os

from textual.app import App, ComposeResult
from textual.widgets import Input, Footer, Header, TextArea
from textual.binding import Binding

# NanoEditor is a simple text editor app using Textual
class NanoEditor(App):
    # Key bindings for editor actions
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
        self.filename = filename  # File to edit
        # Load file content at initialization
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                initial_content = f.read()
        else:
            initial_content = ""
        self.text_area = TextArea(text=initial_content)  # Set initial value here
        self.input_widget = None  # For modal input

    def compose(self) -> ComposeResult:
        # Compose the UI: header, text area, footer
        yield Header()
        yield self.text_area
        yield Footer()

    def on_mount(self):
        # No need to set self.text_area.value here anymore
        pass

    def action_save(self):
        # Save the current text area content to file
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(self.text_area.value)
        self.bell()  # Give feedback (beep)

    def action_search(self):
        # Start a search by showing an input box
        self.show_input("Search:", self.perform_search)

    def perform_search(self, search_term):
        # Search for the term and move cursor if found
        if search_term:
            index = self.text_area.value.find(search_term)
            if index != -1:
                # Move cursor to found index (Textual API may differ)
                self.text_area.cursor_position = index
                # self.text_area.scroll_to_cursor()  # If available
            else:
                self.bell()  # Not found feedback

    def action_search_and_replace(self):
        # Start search and replace by showing input
        self.show_input("Search:", self.perform_search_and_replace)

    def perform_search_and_replace(self, search_term):
        # After getting search term, ask for replace term
        if search_term:
            self._search_term = search_term
            self.show_input("Replace with:", self.do_replace)

    def do_replace(self, replace_term):
        # Replace all occurrences of search_term with replace_term
        if hasattr(self, '_search_term') and replace_term is not None:
            self.text_area.value = self.text_area.value.replace(self._search_term, replace_term)
            self.bell()  # Feedback
            del self._search_term

    def action_goto(self):
        # Show input to go to a specific line
        self.show_input("Go to line:", self.perform_goto)

    def perform_goto(self, line_number):
        # Move cursor to the start of the given line number
        try:
            line_number = int(line_number) - 1  # Convert to zero-based index
            lines = self.text_area.value.splitlines()
            if 0 <= line_number < len(lines):
                # Calculate character index for the start of the line
                index = sum(len(l) + 1 for l in lines[:line_number])
                self.text_area.cursor_position = index
            else:
                self.bell()  # Out of range
        except ValueError:
            self.bell()  # Invalid input

    def action_undo(self):
        # Undo last change if possible (Textual API may differ)
        if hasattr(self.text_area, 'undo'):
            self.text_area.undo()
        else:
            self.bell()

    def action_redo(self):
        # Redo last undone change if possible (Textual API may differ)
        if hasattr(self.text_area, 'redo'):
            self.text_area.redo()
        else:
            self.bell()

    def action_quit(self):
        # Exit the application
        self.exit()

    def show_input(self, prompt, callback):
        # Helper to show an Input widget for user input
        if self.input_widget:
            self.input_widget.remove()
        self.input_widget = Input(placeholder=prompt)
        self.input_widget.display = True
        self.input_widget.styles.width = 40
        self.input_widget.styles.margin = (1, "auto")
        self.input_widget.styles.dock = "top"
        self.input_widget.styles.background = "#222"
        self.input_widget.styles.color = "#fff"
        self.input_widget.styles.border = ("heavy", "blue")
        self.input_widget.handlers = {
            "submitted": lambda event: self._on_input_submit(event, callback)
        }
        self.mount(self.input_widget)
        self.input_widget.focus()

    def _on_input_submit(self, event, callback):
        # Called when user submits input
        value = event.value
        self.input_widget.remove()
        self.input_widget = None
        callback(value)

# Entry point for running the editor

def main():
    if len(sys.argv) < 2:
        print("Usage: tini <filename>")
        sys.exit(1)
    filename = sys.argv[1]
    app = NanoEditor(filename)
    app.run()
