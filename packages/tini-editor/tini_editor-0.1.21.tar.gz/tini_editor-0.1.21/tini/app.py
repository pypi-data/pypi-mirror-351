# tini.py
import sys
import os

from textual.app import App, ComposeResult
from textual.widgets import Input, Footer, Header, TextArea
from textual.binding import Binding

# TiniEditor is a simple text editor app using Textual
class TiniEditor(App):
    # Key bindings for editor actions
    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+q", "quit", "Quit"),
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
            f.write(self.text_area.text)
        # Only beep if something goes wrong (no bell here on success)

    def action_quit(self):
        # Exit the application
        self.exit()

    def show_input(self, prompt, callback):
        # Helper to show an Input widget for user input
        if self.input_widget:
            self.input_widget.remove()
        self.input_widget = Input(placeholder=prompt, id="modal_input")
        self.input_callback = callback  # Store callback for later use
        self.input_widget.display = True
        self.input_widget.styles.width = 40
        self.input_widget.styles.margin = 1  # Use integer for all sides
        self.input_widget.styles.dock = "top"
        self.input_widget.styles.background = "#222"
        self.input_widget.styles.color = "#fff"
        self.input_widget.styles.border = ("heavy", "blue")
        self.mount(self.input_widget)
        self.input_widget.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Called when user submits input (presses Enter)
        if self.input_widget and event.input is self.input_widget:
            value = event.value
            self.input_widget.remove()
            self.input_widget = None
            if hasattr(self, 'input_callback') and self.input_callback:
                self.input_callback(value)
                self.input_callback = None

# Entry point for running the editor

def main():
    if len(sys.argv) < 2:
        print("Usage: tini <filename>")
        sys.exit(1)
    filename = sys.argv[1]
    app = TiniEditor(filename)
    app.run()
