from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static, Header
from textual.containers import Center, Container

from rich_pixels import Pixels

from system.gui.custom_widgets.intermediate_progress import IndeterminateProgress
from system.gui.custom_widgets.image import Image
from system.console import console_bounds


class LoadingScreen(Screen):
    """
    A loading screen for SwiftOS.
    """
    
    CSS = """
    #loading_logo {
        width: auto;
        content-align: center top;
    }
    
    .center {
        content-align: center middle;
        min-width: 100%;
    }
    """
    
    def compose(self) -> ComposeResult:
        
        yield Header(show_clock=True)
        
        with Center():
            width = console_bounds().columns
            image_scale = int(width * 0.272108844)
            
            yield Image("system/assets/images/gui/logo.png", (image_scale, image_scale), classes="center")
            
            yield Static("[bold]Welcome to SwiftOS.[/bold]", classes="center")
            yield IndeterminateProgress(classes="center")