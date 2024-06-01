from system.gui.desktop_screen import Desktop
from system.gui.custom_widgets import window

def execute(desktop: Desktop, args: list[str]):
    windows = desktop.query_one("#windows")
    
    notepad_window = window.Window(title="Notepad")
    windows.mount(notepad_window)
    
    desktop.notify("Notepad running!")