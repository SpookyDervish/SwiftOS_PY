from textual.app import ComposeResult
from textual.widgets import Static

from system.gui.custom_widgets import image, window


class Icon(Static):
    DEFAULT_CSS = """
    Icon {
        width: 10;
        margin: 1;
    }
    
    Icon Static {
        text-align: center;
    }
    """
    
    def __init__(self, text: str = "", icon_path: str | None = None, name: str | None = None, id: str | None = None, classes: str | None = None, disabled: bool = False) -> None:
        """An icon widget, that comes with text and an image. Intended for use on the desktop.

        Args:
            text (str, optional): The text to appear below the icon's image. Defaults to "".
            icon_path (str | None, optional): The file path to the icon. Defaults to None, meaning there will be no image.
            name (str | None, optional): The name of the widget. Defaults to None.
            id (str | None, optional): The id of the widget in the DOM. Defaults to None.
            classes (str | None, optional): The CSS classes for the widget. Defaults to None.
            disabled (bool, optional): Whether the widget is disabled or not. Defaults to False.
        """
        
        self.text = text
        self.icon_path = icon_path
        
        super().__init__("", name=name, id=id, classes=classes, disabled=disabled)
        
    def compose(self) -> ComposeResult:
        yield image.Image(self.icon_path, (10, 10))
        yield Static(self.text)