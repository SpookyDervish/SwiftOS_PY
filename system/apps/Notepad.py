import os

from system.gui.desktop_screen import Desktop
from system.gui.custom_widgets import window, dialog
from system.fs import get_file_extension

from textual.widgets import TextArea, Footer, Static
from textual.binding import Binding


class NotepadWindow(window.Window):    
    BINDINGS = [
        Binding("ctrl+s", "save", "Save file", priority=True)
    ]
    
    def action_save(self):
        text_area = self.query_one(TextArea)
        
        try:
            f = open(self.ARGS[0], "w")
            f.write(text_area.text)
            f.close()
        except Exception as e:
            dialog.create_dialog(
                str(e),
                self.screen,
                "Failed to save file!",
                icon=dialog.DialogIcon.CRITICAL
            )
    
    def on_ready(self):
        desktop = self.screen
        
        ext = None
        
        TEXT = ""
        if len(self.ARGS) > 0:
            
            if os.path.isfile(self.ARGS[0]):
                f = open(self.ARGS[0])
                TEXT = f.read()
                f.close()
        
                ext = get_file_extension(self.ARGS[0])
                if ext == "txt":
                    ext = None
                elif ext == "py":
                    ext = "python"
        
        yield TextArea(TEXT, language=ext, theme="css", show_line_numbers=True)
        yield Footer()


def execute(desktop: Desktop, args: list[str]):
    windows = desktop.query_one("#windows")
    window_bar = desktop.query_one("#window-bar")
    
    notepad_window = NotepadWindow(title="Notepad", size=[75, 18])
    notepad_window.ARGS = args
    
    desktop.add_to_window_bar(notepad_window, window_bar)
    windows.mount(notepad_window)