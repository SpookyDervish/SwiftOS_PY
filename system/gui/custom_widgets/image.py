from textual.widgets import Static

from rich_pixels import Pixels


class Image(Static):
    def __init__(self, file_path: str, resize: tuple[int, int] | None = None, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        """A Textual widget of an image.

        Args:
            file_path (str): The file path to the image.
            resize (tuple[int, int] | None, optional): How many characters wide and tall the image should be resized to. If not passed, the image will be it's default size.
            id (str | None, optional): The ID of the widget in the DOM.
            classes (str | None, optional): The CSS classes for the widget.
        """
        
        self.file_path = file_path
        
        data = Pixels.from_image_path(self.file_path, resize)
        super().__init__(data, name=name, id=id, classes=classes)
        
    def set_image(self, file_path: str, resize: tuple[int, int] | None = None):     
        """Change the image being displayed by this widget.

        Args:
            file_path (str): The file path to the new image to display.
            resize (tuple[int, int] | None, optional): How many characters wide and tall the image should be resized to. If not passed, the image will be it's default size.
        """
        
        self.file_path = file_path   
        data = Pixels.from_image_path(self.file_path, resize)
        
        self.update(data)