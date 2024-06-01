import os

from system.gui.desktop_screen import Desktop
from system.gui.custom_widgets import window, dialog
from system.fs import get_file_extension

from rich.syntax import Syntax

from textual.widgets import TextArea, Footer, Static, DirectoryTree
from textual.containers import VerticalScroll
from textual.binding import Binding

class NotepadWindow(window.Window):    
    DEFAULT_CSS = """
    #tree-view {
        dock: left;
        height: 100%;
        margin-top: 1;
        overflow: auto;
        scrollbar-gutter: stable;
        width: auto;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+shift+s", "save_as", "Save as")
    ]
    
    def action_save(self):
        text_area = self.query_one(TextArea)
        
        try:
            f = open(self.open_file, "w")
            f.write(text_area.text)
            f.close()
        except Exception as e:
            dialog.create_dialog(
                str(e),
                self.screen,
                "Failed to save file!",
                icon=dialog.DialogIcon.CRITICAL
            )
    
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        event.stop()
        code_view = self.query_one("#code-view", TextArea)
        
        self.open_file = event.path
        
        try:
            f = open(self.open_file, "r")
        except FileNotFoundError:
            dialog.create_dialog(
                "File not found.",
                self.screen,
                "Couldn't Open File",
                icon=dialog.DialogIcon.EXCLAMATION
            )
            return
        contents = f.read()
        f.close()
        
        code_view.text = contents
        code_view.language = self.file_path_to_lang(self.open_file)
        
        #self.set_title(str(os.path.basename(event.path)))
    
    def file_path_to_lang(self, file_path: str):
        ext = get_file_extension(file_path)
        
        extensions = {
            "py": "python",
            "md": "markdown",
            "json": "json",
            "css": "css",
            "tcss": "css",
            "html": "html",
            "htm": "html",
            "js": "javascript",
            "java": "java",
            "sh": "bash",
            "go": "go"
        }
        
        try:
            ext = extensions[ext]
        except KeyError:
            ext = None
            
        return ext
    
    def on_ready(self):
        self.open_file = None
        
        ext = None
        
        TEXT = ""
        if len(self.ARGS) > 0:
            
            if os.path.isfile(self.ARGS[0]):
                self.open_file = self.ARGS[0]
                
                f = open(self.open_file)
                TEXT = f.read()
                f.close()
        
                ext = self.file_path_to_lang(self.ARGS[0])
        
        path = os.getcwd() if len(self.ARGS) < 1 else os.path.dirname(self.open_file)
        yield DirectoryTree(path, id="tree-view")
        
        with VerticalScroll():
            yield TextArea(TEXT, language=ext, theme="dracula", show_line_numbers=True, soft_wrap=False, id="code-view")
        yield Footer()


async def execute(desktop: Desktop, args: list[str]):
    windows = desktop.query_one("#windows")
    window_bar = desktop.query_one("#window-bar")
    
    title = "Notepad | "
    if len(args) > 0:
        file_name = os.path.basename(args[0])
        title += file_name
    else:
        title += "New File"
    
    notepad_window = NotepadWindow(title=title, size=[75, 18])
    notepad_window.ARGS = args
    
    await desktop.add_to_window_bar(notepad_window, window_bar)
    windows.mount(notepad_window)