from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, Button
from textual.containers import Horizontal

from system.gui.custom_widgets.window import Window
from system.gui.custom_widgets.image import Image

from enum import Enum


class InvalidButtonsId(Exception):
    def __init__(self, message, buttons_id, *args) -> None:
        self.message = message
        self.buttons_id = buttons_id
        
        super().__init__(str(self.buttons_id))

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
        
        Dialog Image {
            margin-top: 2;
            margin-left: 1;
        }
        
        Dialog #text {
            text-align: right;
            padding-right: 6;
            dock: right;
            margin-top: 5;
            max-width: 50;
        }
        """
    
    def __init__(self, *children: Widget, message: str, title: str = "Message", buttons: DialogButtons = DialogButtons.OK, icon: DialogIcon = DialogIcon.INFO, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        self.message = message
        
        self.buttons = buttons
        self.icon = icon
        
        self.chosen_option = None
        self.closed = False
        
        min_width = 35
        width = max(min_width, len(self.message)+35)
        
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
            raise InvalidButtonsId(f"Invalid DialogButtons id: ", self.buttons)
        
        icons = {
            DialogIcon.INFO:        "system/assets/images/icons/dialog/help.png",
            DialogIcon.QUESTION:    "system/assets/images/icons/dialog/help.png",
            DialogIcon.EXCLAMATION: "system/assets/images/icons/dialog/help.png",
            DialogIcon.CRITICAL:    "system/assets/images/icons/dialog/help.png",
        }
        self._icon_path = icons[self.icon]
        
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
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.chosen_option = "None"
            self.app.log(f"Dialog closed (ID={self.id}, TITLE={self.title}, CHOSEN={self.chosen_option})..")
            self.delete_animation()
            self.closed = True
        elif event.button.id == "minimize":
            self.minimize_animation()
        elif event.button.id == "maximize":
            self.maximize_animation()
        else:
            self.chosen_option = event.button.label.plain
            self.app.log(f"Dialog closed (ID={self.id}, TITLE={self.title}, CHOSEN={self.chosen_option})..")
            self.delete_animation()
            self.closed = True