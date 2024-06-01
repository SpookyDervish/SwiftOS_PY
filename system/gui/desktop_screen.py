import os

from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Header, Footer, Static, TabbedContent, TabPane, Tabs
from textual.containers import Container
from textual import events, on, work

from string import punctuation

from system.gui.custom_widgets import image, window, icon
from system.users import get_user_background
from system.fs import get_file_icon
from system.console import console_bounds


class Desktop(Screen):
    DEFAULT_CSS = """ 
    Screen {
        layers: background foreground;
    }
       
    #windows {
        background: transparent;
        dock: top;
        margin-top: 4;
    }
    
    #windows Icon, #windows Image {
        dock: top;
    }
    
    #windows Window {
        layer: foreground;
    }
    
    Icon {
        layer: foreground;
    }
    
    #window-bar {
        dock: top;
        layout: horizontal;
        max-height: 3;
        
        layer: foreground;
        margin-top: 1;
    }
    """
    
    def __init__(self, logged_in_user: str) -> None:
        """A desktop screen for SwiftOS.

        Args:
            logged_in_user (str): The username of the currently logged in user.
        """
        
        super().__init__()
        
        self.logged_in_user = logged_in_user
        self.selected_window = None
        
        self.__mouse_pos = (0, 0)
    
    @work()
    async def remove_window(self, removed_window) -> None:
        """Remove a window from the desktop.

        Args:
            removed_window (Window): The window to remove.
        """
        
        window_bar: TabbedContent = self.query_one("#window-bar")
        
        window_bar.active = ""
        
        win_id = self.window_title_to_id(removed_window.title)
        window_bar.remove_pane(win_id)
        
        self.windows.query_one(f"#{removed_window.id}").remove()
        
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
            selected_window.normal_size_animation()

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
        
        self.windows.move_child(selected_window, after=-1)
        
        self.selected_window = selected_window
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
    
    async def deselect_window(self, selected_window) -> None:
        """
        Give a visual indicator that a window is not selected.

        Args:
            selected_window (Window): The window to deselect.
        """
        selected_window.set_as_secondary()
        
        win_id = self.window_title_to_id(selected_window.title)
        
        window_bar: TabbedContent = self.query_one("#window-bar")
        pane = window_bar.get_pane(win_id)
        
        window_bar.remove_pane(pane.id)
        pane.remove()
        
        # This basically checks if the selected_window is self.selected_window,
        # if they're the same self.selected_window is set to None.
        self.selected_window = None if self.selected_window == selected_window else self.selected_window 
        
        self.app.log(f"Window Deselected ({self}): {selected_window.id}")
    
    def on_ready(self) -> ComposeResult:
        """
        Overwritable placeholder method for when the Desktop is fully
        initialized.
        
        This should return Textual widgets using `yield` to add to the desktop.
        """
        pass

    def add_to_window_bar(self, window, window_bar: TabbedContent):
        window_title = window.title
        
        new_pane = TabPane(window_title, id=self.window_title_to_id(window_title))
        
        if len(window_bar.children) > 0:
            try:
                window_bar.add_pane(
                    new_pane
                )
                self.app.log("sup")
            except Exception as e: # Duplicate tab id
                self.app.log(e)
                self.app.log(f"Failed to add Window to Window Bar: ({window_bar}): {window}): Window already exists in window bar.")
        else:
            self.app.log("👍")
            return new_pane
        
        self.app.log(f"Window Added to Window bar ({window_bar}): {window}")
    
    def compose(self) -> ComposeResult:
        with Header(show_clock=True):
            yield Static(self.logged_in_user)
            
        
        bounds = console_bounds()
            
        
        
        self.windows = Container(id="windows")
        
        window_bar_windows = []
        
        with self.windows:            
            yield image.Image(get_user_background(self.logged_in_user), (bounds.columns, (bounds.lines*2)-9), id="desktop-background")
            
            for file in os.listdir(f"home/{self.logged_in_user}/Desktop"):
                path = os.path.join(f"home/{self.logged_in_user}/Desktop", file)
                
                new_icon = icon.Icon(path, file, get_file_icon(file))
                yield new_icon
            
            ready_result = self.on_ready(self)
            if ready_result:
                for widget in ready_result:
                    yield widget
                    
                    if isinstance(widget, window.Window):
                        window_bar_windows.append(widget)
                        self.app.log(f"Window Added to Desktop ({self}): ID={widget.id}")
        
        with TabbedContent(id="window-bar") as tabs:
            yield TabPane("Desktop")
            
            for win in window_bar_windows:
                yield self.add_to_window_bar(win, tabs)
                

        self.app.log("Desktop ready!")