from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, Button
from textual.containers import Horizontal
from textual.message import Message
from textual import work, on

from system.gui.custom_widgets.window import Window
from system.gui.custom_widgets.image import Image

from enum import Enum


class InvalidButtonsId(Exception):
    def __init__(self, message, buttons_id, *args) -> None:
        self.message = message
        self.buttons_id = buttons_id
        
        super().__init__(str(self.buttons_id))
        
class InvalidIconId(Exception):
    def __init__(self, message, icon_id, *args) -> None:
        self.message = message
        self.icon_id = icon_id
        
        super().__init__(str(self.icon_id))

class DialogButtons(Enum):
    OK = 1
    YES_NO = 2
    OK_CANCEL = 3
    YES_NO_CANCEL = 4
    ABORT_RETRY_IGNORE = 5
    RETRY_CANCEL = 6
    
class DialogIcon(Enum):
    INFO = 1
    QUESTION = 2
    EXCLAMATION = 3
    CRITICAL = 4

class Dialog(Window):    
    DEFAULT_CSS = """
    Dialog #buttons-list {
        background: $background;
        align: right middle;
        padding-right: 2;
        height: 5;
        dock: bottom;
        margin-bottom: 3;
    }
    
    Dialog #buttons-list Button {
        margin-left: 1;
    }
    
    Dialog Image {
        margin-top: 2;
        margin-left: 1;
    }
    
    Dialog #text {
        text-align: left;
        margin-left: 16;
        dock: left;
        margin-top: 4;
        max-width: 50;
    }
    """
    
    class Submitted(Message):
        """Fired when the user closes or presses a button on the dialog box."""
        def __init__(self, button: str) -> None:
            self.button = button
            super().__init__()
    
    def __init__(self, *children: Widget, message: str, title: str = "Message", buttons: DialogButtons = DialogButtons.OK, icon: DialogIcon = DialogIcon.INFO, name: str | None = None, id: str | None = None, classes: str | None = None, callback = None) -> None:
        """Initialize a dialog. If you want to display a dialog to the Desktop, use the `create_dialog` method.

        Args:
            message (str): The message to display on the dialog window.
            title (str, optional): The title of the window. Defaults to "Message".
            buttons (DialogButtons, optional): What buttons should be available on the dialog. Defaults to DialogButtons.OK.
            icon (DialogIcon, optional): The dialog icon to use. Defaults to DialogIcon.INFO.
            name (str | None, optional): _description_. Defaults to None.
            id (str | None, optional): _description_. Defaults to None.
            classes (str | None, optional): _description_. Defaults to None.

        Raises:
            InvalidButtonsId: Raised if the provided buttons are invalid.
            InvalidIconId: Raised if the provided icon is invalid.
        """
        
        self.message = message
        
        self.buttons = buttons
        self.icon = icon
        
        self.chosen_option = None
        self.closed = False
        
        self._callback = callback
        
        min_width = 30
        width = max(min_width, (len(self.message)/2)+12)
        
        buttons_list = []
        if self.buttons == DialogButtons.OK:
            buttons_list.append(Button("Ok"))
        elif self.buttons == DialogButtons.YES_NO:
            buttons_list.append(Button("Yes"))
            buttons_list.append(Button("No"))
        elif self.buttons == DialogButtons.OK_CANCEL:
            buttons_list.append(Button("Ok"))
            buttons_list.append(Button("Cancel"))
        elif self.buttons == DialogButtons.OK_CANCEL:
            buttons_list.append(Button("Abort"))
            buttons_list.append(Button("Retry"))
            buttons_list.append(Button("Ignore"))
        elif self.buttons == DialogButtons.RETRY_CANCEL:
            buttons_list.append(Button("Retry"))
            buttons_list.append(Button("Cancel"))
        else:
            raise InvalidButtonsId(f"Invalid buttons: ", self.buttons)
        
        icons = {
            DialogIcon.INFO:        "system/assets/images/icons/dialog/info.png",
            DialogIcon.QUESTION:    "system/assets/images/icons/dialog/help.png",
            DialogIcon.EXCLAMATION: "system/assets/images/icons/dialog/caution.png",
            DialogIcon.CRITICAL:    "system/assets/images/icons/dialog/error.png",
        }
        try:
            self._icon_path = icons[self.icon]
        except KeyError:
            raise InvalidIconId(f"Invalid icon: ", self.icon)
        
        super().__init__(
            Image(self._icon_path, (12, 12)),
            Static(self.message, id="text"),
            Horizontal(
                *buttons_list,
                id="buttons-list"
            ),
            title=title,
            size=[width, 13], name=name, id=id, classes=classes,
            title_bar_options=(True, True, False)
        )
        
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.chosen_option = "None"
            self.app.log(f"Dialog closed (ID={self.id}, TITLE={self.title}, CHOSEN={self.chosen_option})..")
            self.closed = True
            
            self.post_message(self.Submitted(self.chosen_option))
        else:
            self.chosen_option = event.button.label.plain
            self.app.log(f"Dialog closed (ID={self.id}, TITLE={self.title}, CHOSEN={self.chosen_option})..")
            
            self.post_message(self.Submitted(self.chosen_option))
            
            if self._callback:
                await self._callback(self.chosen_option)
                
            self.closed = True
            self.delete_animation()
            
        
            
async def create_dialog(message: str, desktop, title: str = "Message", buttons: DialogButtons = DialogButtons.OK, icon: DialogIcon = DialogIcon.INFO, callback = None):
    dialog = Dialog(
        message=message,
        title=title,
        buttons=buttons,
        icon=icon,
        callback=callback
    )
    
    windows = desktop.query_one("#windows")
    window_bar = desktop.query_one("#window-bar")
    
    windows.mount(dialog)
    
    await desktop.add_to_window_bar(dialog, window_bar)
    
    return dialog