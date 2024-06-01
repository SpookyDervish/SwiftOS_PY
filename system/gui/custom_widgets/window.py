from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widget import Widget
from textual.widgets import Static, Button

from textual import events, on, work
from textual.css.scalar import ScalarOffset, Scalar, Unit

from string import ascii_letters
from secrets import choice
from time import sleep

from system.console import console_bounds
from system.gui.desktop_screen import Desktop


def generate_random_string(length: int):
    characters = ascii_letters
    return ''.join(choice(characters) for _ in range(length))

class Window(Vertical):
    DEFAULT_CSS = """
    Window {
        background: $boost;
        dock: left;
    }
    
    Window #title-bar {
        width: 100%;
        height: 1;
        background: grey;
        dock: top;
        
        layout: horizontal;
    }
    
    Window #title-bar #title {
        text-align: right;
        margin-right: 1;
    }
    
    #title-bar-buttons {
        layout: horizontal;
        dock: left;
        max-width: 9;
    }
    
    Window #title-bar .title-button {
        max-height: 1;
        min-width: 2;
    }
    """
    
    def __init__(
        self,
        *children: Widget,
        title: str,
        size: list[int] | None = None,
        start_position: list[int] | None = None,
        title_bar_options: tuple[bool] = (True, True, True),
        no_title_bar: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False
    ) -> None:
        """A window on the desktop.

        Args:
            title (str): The title displayed on the window's title bar.
            size (list[int] | None, optional): How many characters wide and tall the window is. Defaults to 50x12.
            start_position (list[int] | None, optional): The position of the window when it's first created. Defaults to the center of the screen.
            title_bar_options (tuple[bool], optional): A tuple of which title bar buttons should be enabled. (Order: Close, Minimize, Maximize). Defaults to all buttons enabled.
            no_title_bar (bool, optional): If true, the window will have no title bar.
            name (str | None, optional): The name of the widget. Defaults to None.
            id (str | None, optional): The id of the widget in the DOM. Defaults to None.
            classes (str | None, optional): The CSS classes for the widget. Defaults to None.
            disabled (bool, optional): Whether the widget is disabled or not. Defaults to False.
        """
        
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self._title = title
        
        self.window_running = True
        self.no_title_bar = no_title_bar
        
        self.title = title
        self.id = self.id if id is not None else generate_random_string(5)
        
        bounds = console_bounds()
        
        self.window_size = size if size is not None else [50, 12] 
        """else [
            int(bounds.columns * 0.23696682464454977), # These numbers may look weird, but at a resolution of 211x53 characters
            int(bounds.lines   * 0.22641509433962265)  # the window is 50x12 characters wide and tall
        ] """
        
        
        self.position = start_position if start_position is not None else [
            int(bounds.columns/2) - int(self.window_size[0]/2),
            int(bounds.lines/2) - int(self.window_size[1]/2)
        ]
        
        self.is_dragging = False
        
        self.title_bar_options = title_bar_options
        
        self.styles.width = self.window_size[0]
        
        if not self.no_title_bar:
            self.styles.height = self.window_size[1]+1 # We need to add one to make to space for the title bar
        else:
            self.styles.height = self.window_size[1]
        
        self.window_container: Container = self.parent
        
        self.is_maximised = False
        self.is_minimized = False
    
    def set_as_primary(self):
        """Set this window as the selected window.
        """        
        self.focus()
        
        if not self.no_title_bar:
            title_bar = self.query_one("#title-bar")
            title_bar_buttons = title_bar.query_one("#title-bar-buttons")
            
            title_bar.styles.background = "cornflowerblue"
            title_bar_buttons.styles.background = "cornflowerblue"
    
    def set_as_secondary(self):
        """Set this window as the non-selected window.
        """
        if not self.no_title_bar:
            title_bar = self.query_one("#title-bar")
            title_bar_buttons = title_bar.query_one("#title-bar-buttons")
            
            title_bar.styles.background = "grey"
            title_bar_buttons.styles.background = "grey"
    
    def set_title(self, new_title: str):
        """Sets the window's title.

        Args:
            new_title (str): The new title for the window.

        Returns:
            str: The old window title.
        """
        
        self._title = new_title
        self.title = new_title
        
        if not self.no_title_bar:
            title_bar = self.query_one("#title-bar")
            title_text = title_bar.query_one("#title")
            
            old_text = title_text.renderable.plain
            
            title_text.update(f"[bold]{new_title}[/bold] ")
        
        return old_text
    
    def on_leave(self):
        """Handle when the mouse leaves the window."""
        self.is_dragging = False
        
    def on_enter(self):
        """Handle when the mouse enters the window."""
        self.is_dragging = False
        
    def on_mouse_down(self):
        """Handle when the left mouse button begins to be held on the window."""
        self.is_dragging = True
        
        self.screen.select_window(self)
    
    def on_mouse_up(self):
        """Handle when the left mouse button stops being held on the window."""
        self.is_dragging = False
        
    def is_inside_window(self, position: tuple[int, int]):
        """Check is a position on the screen is within the bounds of the window.

        Args:
            position (tuple[int, int]): The postition to be checked within the window.

        Returns:
            bool: Whether the position is within the bounds of the window.
        """
        
        x, y = position
        
        if self.is_maximised == False:
            x1, y1 = (self.position[0], self.position[1])
            
            padding = 4 if not self.no_title_bar else 3
            x2, y2 = (self.position[0] + self.window_size[0], self.position[1] + self.window_size[1] + padding)
            
            if x >= x1 and x <= x2 and y >= y1 and y <= y2:
                return True
            else:
                return False
        else:
            bounds = console_bounds()
            
            if y > 3 and y < bounds.lines-1:
                return True
            else:
                return False
            
    @work(thread=True)
    def normal_size_animation(self):
        """
        Play an animation of the window going to its normal size and position.
        """
        
        self.window_running = False
        
        self.is_maximised = False
        self.is_minimized = False
                
        self.styles.animate("width", value=self.window_size[0], duration=1/3)
        self.styles.animate("height", value=self.window_size[1]+1, duration=1/3)
        
        """self.position = [
            position[0],   #- self.window_size[0]/2,
            position[1] #- self.window_size[1]/2
        ]"""
        
        new_offset = ScalarOffset(
            Scalar(self.position[0], Unit(1), Unit(1)),
            Scalar(self.position[1], Unit(1), Unit(1))
        )
        
        self.styles.animate("offset", value=new_offset, duration=1/3)
        sleep(1/3)
        self.window_running = True
        
    def on_mouse_move(self, event: events.MouseMove) -> None:
        """
        Handle when the mouse moves over the window.
        
        ! This is used internally by Textual, do not use this in the rest of the OS.

        Args:
            event (events.MouseMove): The event passed by Textual.
        """
        
        #self.set_title(f"X: {event.screen_x}, Y: {event.screen_y} | TOPL: {self.position}, BOTR: {(self.position[0] + self.window_size[0], self.position[1] + self.window_size[1])} | {self.is_inside_window((event.screen_x, event.screen_y))}")
        
        if not self.window_running:
            return
        
        if not self.is_inside_window((event.screen_x, event.screen_y)):
            self.is_dragging = False
        
        if self.is_dragging:
            
            if self.is_maximised:
                self.styles.width = self.window_size[0]
                
                if not self.no_title_bar:
                    self.styles.height = self.window_size[1] + 1
                else:
                    self.styles.height = self.window_size[1]
                
                self.position = [
                    event.screen_x - self.window_size[0]/2,
                    event.screen_y - self.window_size[1]/2 - 3
                ]
                
                self.styles.offset = tuple(self.position)
                
                self.is_maximised = False
            else:
                self.position = [
                    self.position[0] + event.delta_x,
                    self.position[1] + event.delta_y
                ]
                
                self.styles.offset = (
                    self.position[0], # Top
                    self.position[1]  # Left
                )
    
    @work(thread=True)
    def minimize_animation(self):
        """Play an animation of the window shrinking and going to the top left corner of the screen.
        """
        
        self.window_running = False
        
        self.set_as_secondary()
        
        if not self.is_maximised:
            self.is_minimized = True
            
            self.styles.animate("width", value=0, duration=1/3)
            self.styles.animate("height", value=0, duration=1/3)
            
            new_offset = ScalarOffset(
                Scalar(0, Unit(1), Unit(1)),
                Scalar(0, Unit(1), Unit(1))
            )
            
            self.styles.animate("offset", value=new_offset, duration=1/3)
        else:
            self.normal_size_animation(self.position)
            
    @work(thread=True)
    def maximize_animation(self):
        """Play an animation of the window becoming maximized.
        """
        
        self.window_running = False
        
        bounds = console_bounds()
        
        self.styles.animate("width", value=bounds.columns, duration=1/3)
        self.styles.animate("height", value=bounds.lines-5, duration=1/3)
        
        new_offset = ScalarOffset(
            Scalar(0, Unit(1), Unit(1)),
            Scalar(0, Unit(1), Unit(1))
        )
        self.styles.animate("offset", value=new_offset, duration=1/3)
        
        self.is_maximised = True
        sleep(1/3)
        self.window_running = True
            
    @work(thread=True)
    def delete_animation(self):
        """Play a shrinking animation and delete the window.
        """
        
        self.window_running = False
        
        self.styles.animate("width", value=0, duration=1/3)
        self.styles.animate("height", value=0, duration=1/3)
        
        new_offset = ScalarOffset(
            Scalar(self.position[0] + self.size.width/2, Unit(1), Unit(1)),
            Scalar(self.position[1] + self.size.height/2, Unit(1), Unit(1))
        )
        
        self.styles.animate("offset", value=new_offset, duration=1/3)
        
        #self.query_one("#title-bar").styles.animate("height", value=0, duration=1.0)
        sleep(1/3 + 0.25)
        #try:
        self.parent.parent.remove_window(self)
        """except RuntimeError:
            # Stop crying and just accept that I'm trying to delete something, smh :/
            pass """
            
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle when a button is pressed on the title bar of the window.
        
        ! This is used internally by Textual, do not use this in the rest of the OS.

        Args:
            event (Button.Pressed): The event passed by Textual.
        """
        
        if event.button.id == "close":
            self.app.log(f"Deleting window ID={self.id}..")
            self.delete_animation()
        elif event.button.id == "minimize":
            self.app.log(f"Minimizing window ID={self.id}..")
            self.minimize_animation()
        elif event.button.id == "maximize":
            self.app.log(f"Maximize window ID={self.id}..")
            self.maximize_animation()
        
    
    def compose(self) -> ComposeResult:
        """
        Compose the window.

        ! This is used internally by Textual, do not use this in the rest of the OS.
        """
        
        self.app.log(f"Creating window (TITLE={self.title}, ID={self.id})..")
        self.styles.offset = (
            self.position[0], # Top
            #0,                # Right
            #0,                # Bottom
            self.position[1]  # Left
        )
        
        
        
        if not self.no_title_bar:
            with Container(id="title-bar"):
                yield Static(f"[bold]{self.title}[/bold] ", id="title")
                
                with Container(id="title-bar-buttons"):
                    close, mini, maxi = self.title_bar_options
                    
                    if close:
                        yield Button("X", variant="error", id="close", classes="title-button")
                    if mini:
                        yield Button("O", variant="warning", id="minimize", classes="title-button")
                    if maxi:
                        yield Button("█", variant="success", id="maximize", classes="title-button")
        
        self.app.log(f"Created window: {self.title}")
        
        
    ### HELPER FUNCTIONS ###
    def __str__(self) -> str:
        state = ""
        if self.is_maximised:
            state = "MAXIMISED"
        elif self.is_minimized:
            state = "MINIMIZED"
        else:
            state = "RESTORED"
        
        return f"(TITLE={self.title}, ID={self.id}, STATE={state})"