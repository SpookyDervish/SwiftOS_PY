"""
# SwiftOS
"""
from textual.app import App, ComposeResult
from textual.widgets import RichLog

from time import sleep
from threading import Thread

from system import console, fs, boot


class SwiftOS(App):
    """
    # SwiftOS
    The entry point for the operating system.
    
    Sets up a textual interface and boots the system.
    """

    BINDINGS = []
    
    ENABLE_COMMAND_PALETTE = False

    def compose(self) -> ComposeResult:
        """Create the basic boot interface."""
        yield RichLog(min_width=console.console_bounds().columns, highlight=True, markup=True, id="boot_log")

    def halt(self, message: bool = False) -> None:
        if message:
            self.query_one(RichLog).write("[bold]Halting..[/bold]")
            
        self.__halted = True
        
    def action_toggle_dark(self) -> None:
        self.dark = not self.dark
        
    def action_safe_mode(self):
        if self.__boot_ready:
            if not self.safe_mode:
                console.log(self.query_one("#boot_log"), "Safe Mode has been enabled!", console.LogLevel.WARNING)
            
            self.safe_mode = True

    def on_ready(self) -> None:
        """
        Begin the boot process.
        """        
        self.__halted = False
        self.__boot_ready = False
        
        self.safe_mode = False
        
        boot_log: RichLog = self.query_one("#boot_log")
        print = boot_log.write

        logo = console.ascii_logo_rainbow()
        
        print(console.center_text(logo))
        print(console.center_text("[bold]Swift[/bold]\n"))
        
        console.rule_line(boot_log, "bold blue")
        
        console.log(boot_log, "Searching for [bold]boot.ini[/bold]..")
        
        boot_ini_path = fs.find_file("boot.ini", "system")
        
        if boot_ini_path == None: # We didn't find boot.ini :(
            console.log(boot_log, "[bold gold1]boot.ini[/bold gold1] was not found!", console.LogLevel.FATAL)
            self.halt(True)
        else:
            console.log(boot_log, f"[bold gold1]boot.ini[/bold gold1] found in [bold magenta]{boot_ini_path}![/bold magenta]")
            
        if self.__halted:
            return
        
        console.log(boot_log, "Booting up kernel..")
        console.log(boot_log, "Making sure that files exist for startup..\n")
        
        self.__boot_ready = True
        
        console.log(boot_log, "Press [bold blue]<S>[/bold blue] within 2 seconds to activate Safe Mode.", console.LogLevel.INFO)
        
        self.__boot_ready = False
        boot.boot(self, boot_ini_path)


if __name__ == "__main__":
    swift_os = SwiftOS()
    
    try:
        swift_os.run()
    except KeyboardInterrupt:
        pass