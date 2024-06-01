from system.gui.desktop_screen import Desktop
from system.gui.custom_widgets import window

def execute(desktop: Desktop, args: list[str]):
    windows = desktop.query_one("#windows")
    window_bar = desktop.query_one("#window-bar")
    
    notepad_window = window.Window(title="Notepad")
    desktop.add_to_window_bar(notepad_window, window_bar)
    windows.mount(notepad_window)