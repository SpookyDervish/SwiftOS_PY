from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Static, TabbedContent, TabPane
from textual.containers import Container
from textual import events, on

from string import punctuation

from system.gui.custom_widgets import image, window
from system.users import get_user_background
from system.console import console_bounds


class Desktop(Screen):
    DEFAULT_CSS = """
    #windows {
        background: $background-lighten-1;
    }
    
    #windows Image {
        dock: top;
    }
    
    #window-bar {
        dock: top;
        margin-top: 1;
        layout: horizontal;
        max-height: 3;
    }
    
    
    """
    
    def __init__(self, logged_in_user: str) -> None:
        """A desktop screen for SwiftOS.

        Args:
            logged_in_user (str): The username of the currently logged in user.
        """
        
        super().__init__()
        
        self.logged_in_user = logged_in_user
        self.__mouse_pos = (0, 0)
        
    def remove_window(self, removed_window) -> None:
        """Remove a window from the desktop.

        Args:
            removed_window (Window): The window to remove.
        """
        
        window_bar: TabbedContent = self.query_one("#window-bar")
        
        window_bar.active = ""
        
        win_id = self.window_title_to_id(removed_window.title)
        window_bar.remove_pane(f"{win_id}")
        
        self.windows.query_one(f"#{removed_window.id}").remove()
        del window
        
        self.app.log(f"Window Removed From Desktop ({self}): {removed_window.id}")
    
    def on_mouse_move(self, event: events.MouseMove) -> None:
        self.__mouse_pos = (event.screen_x, event.screen_y) # Constant mouse tracking :D
    
    def get_window(self, title: str):
        """
        Find a window inside the desktop using it's title.  
        
        ! Probably don't use this, you should find a window using it's id.

        Args:
            title (str): The title of the window you want to find.

        Returns:
            Window | None: Returns the window if it found it, otherwise returns `None`.
        """
        for found_window in self.windows.children:
            if isinstance(found_window, window.Window):
                if found_window.title == title:
                    return found_window
    
    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> bool:  
        """Handle when a tab is clicked on the window bar in the desktop.
        This is handled by `Textual`, this is not intended for use.

        Args:
            event (TabbedContent.TabActivated): The event that will be handled
        """
        for other in self.windows.children:
            if isinstance(other, window.Window):
                other.set_as_secondary()

        window_title = event.tab.renderable.plain
        selected_window: window.Window = self.get_window(window_title)
        
        if not selected_window:
            return
        
        self.select_window(selected_window)
        
        if selected_window.is_minimized:
            selected_window.normal_size_animation(selected_window.position)

    def select_window(self, selected_window) -> None:
        """Give a visual indicator a window is selected.

        Args:
            selected_window (Window): The window to select.
        """
        
        for other in self.windows.children:
            if isinstance(other, window.Window):
                other.set_as_secondary()
        
        self.windows.children[self.windows.children.index(selected_window)].set_as_primary()
        
        window_bar: TabbedContent = self.query_one("#window-bar")
        window_bar.active = self.window_title_to_id(selected_window.title)
        
        self.app.log(f"Window Selected ({self}): {selected_window.id}")
    
    def window_title_to_id(self, title: str):
        """Converts a window title to an id on the window bar.

        Args:
            title (str): The title of the window.

        Returns:
            str: The id of the tab in the window bar.
        """
        no_punctuation = title.translate(
            str.maketrans('', '', punctuation)
        )
        
        return title.replace(" ", "-").lower()
    
    def deselect_window(self, selected_window) -> None:
        """
        Give a visual indicator that a window is not selected.

        Args:
            selected_window (Window): The window to deselect.
        """
        selected_window.set_as_secondary()
        
        win_id = self.window_title_to_id(selected_window.title)
        
        window_bar: TabbedContent = self.query_one("#window-bar")
        window_bar.remove_pane(win_id)
        
        self.app.log(f"Window Deselected ({self}): {selected_window.id}")
    
    def on_ready(self) -> ComposeResult:
        """
        Overwritable placeholder method for when the Desktop is fully
        initialized.
        
        This should return Textual widgets using `yield` to add to the desktop.
        """
        pass
    
    def compose(self) -> ComposeResult:
        with Header(show_clock=True):
            yield Static(self.logged_in_user)
            
        
        bounds = console_bounds()
            
        
        
        self.windows = Container(id="windows")
        
        window_bar_windows = ["Desktop"]
        
        with self.windows:
            yield image.Image(get_user_background(self.logged_in_user), (bounds.columns, (bounds.lines*2)-11), id="desktop-background")
            
            for widget in self.on_ready(self):
                self.app.log(str(widget))
                yield widget
                
                if isinstance(widget, window.Window):
                    window_bar_windows.append(widget.title)
                    self.app.log(f"Window Added to Desktop ({self}): ID={widget.id}")
        
        with TabbedContent(id="window-bar") as tabs:
            for title in window_bar_windows:
                yield TabPane(title, id=self.window_title_to_id(title))
                #self.app.log(f"Window Added to Window bar ({tabs}): (TITLE={widget.title}, ID={widget.id})")
        
        yield Footer()

        self.app.log("Desktop ready!")