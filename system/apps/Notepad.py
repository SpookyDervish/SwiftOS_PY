import os

from system.gui.desktop_screen import Desktop
from system.gui.custom_widgets import window, dialog
from system.fs import get_file_extension

from rich.syntax import Syntax

from textual.widgets import TextArea, Footer, Static, DirectoryTree
from textual.containers import VerticalScroll
from textual.binding import Binding

from textual_fspicker import FileSave, FileOpen

from textual import work

from system.gui.custom_widgets.dialog import create_dialog, DialogButtons, DialogIcon

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
        Binding("ctrl+shift+s", "save_as", "Save as"),
        Binding("ctrl+o", "open", "Open file")
    ]
    
    async def read_file(self, file_path: str):
        new_title = os.path.basename(file_path)
        
        window_bar = self.screen.query_one("#window-bar")
        text_area = self.query_one(TextArea)
        
        f = open(file_path, "r")
        text_area.load_text(f.read())
        f.close()
        
        self.open_file = file_path
        
        text_area.language = self.file_path_to_lang(file_path)
        
        await self.screen.change_window_name(self, new_title, window_bar)
        self.unsaved_changes = False
    
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
            
    async def action_save_as(self):
        text_area = self.query_one(TextArea)
        chosen_file = None
        
        def save_dialog(answer: str):
            if answer == "Yes" and chosen_file:
                with open(str(chosen_file), "w") as f:
                    f.write(text_area.text)
        
        async def on_save(file):
            nonlocal chosen_file
            chosen_file = file
            
            if chosen_file: # If the user didn't press "Cancel"
                if os.path.isfile(chosen_file): # If the user chose an existing file
                    await create_dialog("This file already exists! Do you want to overwrite it?", self.screen, "Save as", buttons=DialogButtons.YES_NO, icon=DialogIcon.QUESTION, callback=save_dialog)
                else:
                    with open(str(chosen_file), "w") as f:
                        f.write(text_area.text)
                
        
        file_save_dialog = FileSave()
        await self.app.push_screen(file_save_dialog, callback=on_save)
    
    def action_open(self):
        text_area = self.query_one(TextArea)
        chosen_file = None
        
        async def unsaved_changes_dialog(answer: str):
            if not chosen_file:
                return
            
            if answer == "Yes": # Save the changes
                with open(self.open_file, "w") as f:
                    f.write(text_area.text)

            await self.read_file(chosen_file)
        
        async def on_open(file):
            nonlocal chosen_file
            chosen_file = file
            
            if file: # If the user didn't press "Cancel"
                if self.unsaved_changes: # If the user has made unsaved changes
                    await create_dialog("You have unsaved changes! Would you like to save them?", self.screen, "Open file", buttons=DialogButtons.YES_NO, icon=DialogIcon.QUESTION, callback=unsaved_changes_dialog)
                else:
                    await self.read_file(file)
        
        file_open_dialog = FileOpen()
        self.app.push_screen(file_open_dialog, callback=on_open)
        
    def on_text_area_changed(self, event: TextArea.Changed):
        self.unsaved_changes = True
    
    """def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
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
        
        #self.set_title(str(os.path.basename(event.path)))"""
    
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
        self.unsaved_changes = False
        
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
        #yield DirectoryTree(path, id="tree-view")
        
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