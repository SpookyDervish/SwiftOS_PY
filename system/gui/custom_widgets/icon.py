from textual.app import ComposeResult
from textual.widgets import Static
from textual.widget import Widget
from textual.containers import Center
from textual import events, on

import time
import os

from system.gui.custom_widgets import image


class Icon(Widget):
    DEFAULT_CSS = """
    Icon {
        visibility: hidden;
        
        width: 11;
        height: 7;
        margin: 1;
    }
        
    Icon Static {
        visibility: visible;
        width: 9;
        margin-left: 1;
        background: transparent;
    }
    """
    
    def __init__(self, associated_file: str, text: str = "", icon_path: str | None = None, name: str | None = None, id: str | None = None, classes: str | None = None, disabled: bool = False) -> None:
        """An icon widget, that comes with text and an image. Intended for use on the desktop.

        Args:
            associated_file (str): The path to the file this icon links with.
            text (str, optional): The text to appear below the icon's image. Defaults to "".
            icon_path (str | None, optional): The file path to the icon. Defaults to None, meaning there will be no image.
            name (str | None, optional): The name of the widget. Defaults to None.
            id (str | None, optional): The id of the widget in the DOM. Defaults to None.
            classes (str | None, optional): The CSS classes for the widget. Defaults to None.
            disabled (bool, optional): Whether the widget is disabled or not. Defaults to False.
        """
        
        self.text = text
        self.icon_path = icon_path if icon_path is not None else "system/assets/images/icons/txt.png"
        
        self.file = associated_file
        self.last_click = 999999999999999 # set it to a really high number to not accidentally open an icon
        
        self.click_threshold = 0.5 # clicks must be within 0.5 seconds to be considered a double click
        
        self.hovered = False
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        
    def open_icon(self):
        if not os.path.isfile(self.file):
            pass
        
    def compose(self) -> ComposeResult: 
        yield image.Image(self.icon_path, (9, 11), id="icon-image")
        yield Static(self.text, id="icon-text")
        
    @on(events.MouseDown)
    def mouse_down(self):
        current_time = time.time()
        
        if current_time - self.last_click <= self.click_threshold:
            # double click!!!!
            
            self.open_icon()
        
        self.last_click = current_time