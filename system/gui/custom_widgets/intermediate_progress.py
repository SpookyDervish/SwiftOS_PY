from textual.widgets import Static

from rich.progress import Progress, BarColumn


class IndeterminateProgress(Static):
    def __init__(self, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        """An indeterminate progress bar Textual widget.

        Args:
            name (str | None, optional): The name of the widget.
            id (str | None, optional): The ID of the widget in the DOM.
            classes (str | None, optional): The CSS classes for the widget.
        """
        
        super().__init__("", name=name, id=id, classes=classes)
        self._bar = Progress(BarColumn())  
        self._bar.add_task("", total=None)

    def on_mount(self) -> None:
        # When the widget is mounted start updating the display regularly.
        self.update_render = self.set_interval(
            1 / 60, self.update_progress_bar
        )  

    def update_progress_bar(self) -> None:
        self.update(self._bar)  
