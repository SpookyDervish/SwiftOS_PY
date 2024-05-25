from textual.screen import Screen, ModalScreen
from textual.app import ComposeResult
from textual.widgets import Header, Static, Input, Button
from textual.containers import Container, Center

from hashlib import sha256
from time import sleep

from system.gui.custom_widgets.image import Image
from system.console import console_bounds
from system import users


class LoginForm(ModalScreen):
    CSS = """
    .center {
        content-align: center middle;
        min-width: 100%;
    }
    """
    
    title = "Login"
    border_title = "Login"
    
    CSS_PATH = "../assets/css/boot.tcss"
    
    def __init__(self, login_screen) -> None:
        """The form for the login screen in SwiftOS.

        Args:
            login_screen (Screen): The screen this from belongs to.
        """
        
        super().__init__(id="login_form")

        
        self.login_screen = login_screen
    
    def compose(self) -> ComposeResult:        
        self.users = users.get_users()
        self.current_user_index = 0
        self.current_user = self.users[self.current_user_index]
        
        theme = users.get_user_details(self.current_user)["theme"]
        
        if theme == "light":
            self.app.dark = False
        elif theme == "dark":
            self.app.dark = True
        
        self.login_screen.set_background(self.current_user)
        
        width = console_bounds().columns   
        image_scale = int(width * 0.136054422)
        
        yield Header(True)
        with Container():
            yield Image(users.get_user_icon(self.current_user), (image_scale, image_scale), classes="center", id="user-icon")
            yield Static(f"\n[bold]{self.current_user}[/bold]", id="username", classes="center")
            
            yield Static("", classes="center", id="status")
            
            with Center(id="password-container"):
                
                yield Input(placeholder="Password", password=True, id="login-password", classes="center")

            with Center(id="sign-in"):
                yield Button("Sign In", variant="success", id="sign-in-button")
                yield Button("Change User", id="change-user")
    
    def sign_in(self):
        """
        Use the entered password in the login form to attempt to sign in.
        
        Using `sha256`, the password is hashed and checked against the user's
        password hash.
        
        If the passwords match the user has logged in successfully, if they don't
        match then the password is incorrect.
        """
        
        sign_in_button = self.query_one("#sign-in-button")
        change_user_button = self.query_one("#change-user")
        password_input: Input = self.query_one("#login-password")
        
        if password_input.value.strip() == "":
            return
        
        sign_in_button.disabled = True
        change_user_button.disabled = True
        password_input.disabled = True
        
        user_details = users.get_user_details(self.current_user)
        password = password_input.value
        
        encrypted_pass = sha256(password.encode()).hexdigest()
        
        status = self.query_one("#status")
        if encrypted_pass == user_details["password_hash"]: # Log in success
            status.update("[bold gold1]Welcome.[/bold gold1]")
            
            async def dismiss_login():
                sleep(2)
                self.dismiss(self.current_user)
            self.app.run_worker(dismiss_login, thread=True)
        else: # Incorrect password
            status.update("[bold red]Incorrect password![/bold red]")
            
            async def unlock_input():
                sleep(1)
                password_input.value = ""
                
                sign_in_button.disabled = False
                change_user_button.disabled = False
                password_input.disabled = False
            self.app.run_worker(unlock_input, thread=True)

    def change_user(self):
        """Change the user being signed in. This cycles through all the users on the system.
        
        TODO: Make a users list rather than cycling through all the users.
        """
        
        sign_in_button = self.query_one("#sign-in-button")
        change_user_button = self.query_one("#change-user")
        password_input: Input = self.query_one("#login-password")
        
        password_input.value = ""
        sign_in_button.disabled = True
        change_user_button.disabled = True
        password_input.disabled = True
        self.query_one("#status").update("")
        
        self.current_user_index += 1
        if self.current_user_index >= len(self.users):
            self.current_user_index = 0
            
        self.current_user = self.users[self.current_user_index]
        
        user_icon = self.query_one("#user-icon")
        width = console_bounds().columns   
        image_scale = int(width * 0.136054422)
        
        self.query_one("#username").update(f"\n[bold]{self.current_user}[/bold]")
        
        user_icon.set_image(users.get_user_icon(self.current_user), (image_scale, image_scale))
        self.login_screen.set_background(self.current_user)
        
        theme = users.get_user_details(self.current_user)["theme"]
        
        if theme == "light":
            self.app.dark = False
        elif theme == "dark":
            self.app.dark = True
        
        sign_in_button.disabled = False
        change_user_button.disabled = False
        password_input.disabled = False
    
    def on_button_pressed(self, event: Button.Pressed):
        """
        Handle when a button is pressed and handled by Textual.
        
        ! Don't use this in actual code, this is handled by Textual and should not be used by the rest of the OS.

        Args:
            event (Button.Pressed): _description_
        """
        
        if event.button.id == "sign-in-button":
            self.sign_in()
        elif event.button.id == "change-user":
            self.change_user()

class LoginScreen(Screen):    
    """A screen to handle logging in inside SwiftOS.
    """
    
    def compose(self) -> ComposeResult:
        yield Header(True)
        
        bounds = console_bounds()
        width = bounds.columns
        height = (bounds.lines*2)-3
        
        yield Image("system/assets/images/backgrounds/1.png", (width, height))
    
    def set_background(self, username: str):
        """Set the background image of the login screen.

        Args:
            username (str): _description_
        """
        
        bounds = console_bounds()
        width = bounds.columns
        height = (bounds.lines*2)-3
        
        self.query_one(Image).set_image(users.get_user_background(username), (width, height))