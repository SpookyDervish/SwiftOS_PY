import os

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, MarkdownViewer, TabbedContent, TabPane, Button, Input, Static
from textual.containers import ScrollableContainer, Center, Grid, Container
from textual.validation import Length
from textual import on

from system.gui.custom_widgets.image import Image
from system.users import get_backgrounds, create_user, change_user, user_exists, get_user_details, get_users
from system.console import console_bounds


class SetupScreen(Screen):
    """
    A screen for setting up a user in SwiftOS.
    """
    
    PAGES = [
        """
# Welcome to Setup!

If this is your first time using SwiftOS, this setup will teach you everything you need to know.
From creating your account, to personalizing your experience, this Setup has everything.

Press **"Next"** to continue.
        """,
        
        """
# Creating Your First Account

We're going to setup your **SwiftOS account**.
First things first, enter your name. This is what will set you apart from other people using your
computer!

## Creating a Password
Now, the most important part, creating a password.

A password should have these things:
- Atleast 8 characters
- Random numbers, letts, and special symbols *(dollar signs, hashtags, etc...)*
- A long length


Things you should **AVOID** when creating a password:
- Personal information
- Common passwords

**Have a go at creating your password!**

Press **"Next"** to continue.
        """,
        
        """
# Personalization

Now you can choose some preferences and customize the look and feel of SwiftOS!
Choose a background and whether you would like to use light or dark theme.

## Backgrounds

Backgrounds show up on your desktop, on the login screen, basically everywhere
personal to you! Choose one that you enjoy looking at, and feel free to change it later.

## Themes

Themes are best used depending on your environment. If you work in a dark environment,
we recommend the dark theme. If you work in a light environment, we recommend the light
theme!

## Profile Pictures

Profile pictures are coming in the future to SwiftOS, watch out for their release!

Press **"Next"** to continue.
        """,
        
        """
# You're all set!

Have fun on your journey into the world of SwiftOS!
If you have any issues or questions, message our Discord! **(13+)**

**Thanks for using SwiftOS!**

*Note: Your computer will restart after pressing "Finish".*

Press **"Finish"** to end Setup.
        """
    ]
    
    CSS_PATH = "../assets/css/setup.tcss"
    CURRENT_TAB = 1
    
    def on_button_pressed(self, event: Button.Pressed):
        """
        Handle the event of a button being pressed.
        
        ! Do not use this in the rest of the OS, this is handled internally by Textual.

        Args:
            event (Button.Pressed): The event passed by Textual.
        """
        
        username = self.query_one("#username-input").value
        
        tabbed_content = self.query_one(TabbedContent)
        
        if event.button.id != "finish-button":
            next_tab_str = f"tab-{self.CURRENT_TAB+1}"
            next_tab = tabbed_content.get_tab(next_tab_str)
        
        if event.button.id == "finish-button": # Finish the setup
            change_user(username, ready=True)
            
            self.dismiss(True)
        elif event.button.id == "next-button": # Go to the next page, if we can
            tabbed_content = self.query_one(TabbedContent)
            
            self.CURRENT_TAB += 1
            if self.CURRENT_TAB == 5:
                self.CURRENT_TAB = 1
            
            new_tab_str = f"tab-{self.CURRENT_TAB}"
            new_tab = tabbed_content.get_tab(new_tab_str)
            
            if new_tab.disabled == False: # We're allowed to continue
                tabbed_content.active = new_tab_str
                
                if new_tab_str == "tab-3" and self.query_one("#username-input").disabled == False: # If we've entered our user's username and password we can continue
                    username_input = self.query_one("#username-input")
                    password_input = self.query_one("#password-input")
                    confirm_password_input = self.query_one("#confirm-password-input")
                    
                    username_input.disabled = True
                    password_input.disabled = True
                    confirm_password_input.disabled = True
                    
                    create_user(username_input.value, password_input.value, True)
                elif new_tab_str == "tab-4":
                    tabbed_content.active = "tab-4"
            else: # Back up, back up, back up
                self.CURRENT_TAB -= 1
        elif event.button.id == "select-background": # Select the specified desktop background
            container = event.button.parent
            image_path = container.query_one("#image").file_path
            
            change_user(username, background=image_path)
            
            details = get_user_details(username)
            
            if details["theme"].strip() != "":
                next_tab.disabled = False
        elif event.button.id == "select-light-theme": # Select the light theme
            change_user(username, theme="light")
            
            details = get_user_details(username)
            
            self.app.dark = False
            
            if details["desktop_background"].strip() != "":
                next_tab.disabled = False
        elif event.button.id == "select-dark-theme": # Select the dark theme
            change_user(username, theme="dark")
            
            details = get_user_details(username)
            
            self.app.dark = True
            
            if details["desktop_background"].strip() != "":
                next_tab.disabled = False
    
    @on(TabbedContent.TabActivated, "#tabs")
    def tab_changed(self):
        """Set the current tab when Textual fires an event saying the current tab has changed.
        """
        tabbed_content = self.query_one(TabbedContent)
        
        self.CURRENT_TAB = int(tabbed_content.active[4])
    
    def on_input_changed(self, event: Input.Changed):
        """
        Fires when the user types a key inside of a text input.
        
        ! This is used internally by Textual, do not use this in the rest of the OS.

        Args:
            event (Input.Changed): The event passed by Textual.
        """
        
        status = self.query_one("#status")
        self.can_continue = False

        def set_error(message):
            nonlocal is_error
            is_error = True
            status.update(f"[bold red]{message}[/bold red]")

        validations = {
            "validation_result": lambda: ( not event.validation_result.is_valid,
                                    event.validation_result.failure_descriptions),
            "empty_password": lambda: (self.query_one("#password-input").value.strip() == "" or 
                                    self.query_one("#confirm-password-input").value.strip() == "",
                                    ["You can't have an empty password!"]),
            "empty_username": lambda: (self.query_one("#username-input").value.strip() == "",
                                    ["You can't have an empty username!"]),
            "password_mismatch": lambda: (event.input.id in ["confirm-password-input", "password-input"] and 
                                        event.input.value != self.query_one("#confirm-password-input" if event.input.id == "password-input" else "#password-input").value,
                                        ["Passwords do not match!"]),
            "username_taken": lambda: (user_exists(self.query_one("#username-input").value),
                                    ["That username is taken!"])
        }

        is_error = False

        for _, validation in validations.items():
            condition, message = validation()
            if condition and len(message) > 0:
                set_error(message[0])
                break

        if not is_error:
            status.update("")
            self.can_continue = True

        tabbed_content = self.query_one(TabbedContent)
        next_tab_str = f"tab-{self.CURRENT_TAB + 1}"
        next_tab = tabbed_content.get_tab(next_tab_str)
        next_tab.disabled = not self.can_continue
        self.can_continue = False
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        initial = "tab-1"
        users = get_users()
        
        if len(users) == 1:
            details = get_user_details(users[0])
            
            if details["theme"] == "light":
                self.dark = False
            elif details["theme"] == "dark":
                self.dark = True
            
            if details["ready"] == False:
                if details["desktop_background"].strip() == "" or details["theme"].strip() == "":
                    initial = "tab-3"
                else:
                    initial = "tab-4"
                
                if details["password_hash"].strip() == "":
                    initial = "tab-2"
                    
                
        
        with TabbedContent(id="tabs", initial=initial):
            with TabPane("Welcome!", disabled=False, classes="container"):
                yield MarkdownViewer(self.PAGES[0], id="info")
                
                with ScrollableContainer(id="setup-form"):
                    
                    
                    yield Button("Next", id="next-button", variant="primary")
            with TabPane("Creating your account.", disabled=False, classes="container") as pane:
                already_done = False
                if initial == "tab-2" or initial == "tab-3" or initial == "tab-4":
                    already_done = True
                
                yield MarkdownViewer(self.PAGES[1], id="info")
                
                with ScrollableContainer(id="setup-form"):
                    yield Image("system/assets/images/user/default_user.png", (20, 20), classes="center")
                    
                    with Center():
                        username_input = Input("", placeholder="Username", id="username-input", max_length=25,
                                    validators=[
                                        Length(3, 25, "The length of your username must be between 3 and 25 characters.")
                                    ])
                        
                        password_input = Input("", placeholder="Password", id="password-input", password=True, max_length=30,
                                    validators=[
                                        Length(8, 30, "The length of your password must be between 8 and 30 characters.")
                                    ])
                        
                        confirm_password_input = Input("", placeholder="Confirm Password", id="confirm-password-input", password=True, max_length=30,
                                    validators=[
                                        Length(8, 30, "The length of your password must be between 8 and 30 characters.")
                                    ])
                        
                        yield username_input
                        yield password_input
                        yield confirm_password_input
                        yield Static("", id="status")
                        
                        if already_done:
                            details = get_user_details(users[0])
                            
                            username_input.value = users[0]
                            username_input.disabled = True
                            password_input.disabled = True
                            confirm_password_input.disabled = True
                            pane.disabled = False
                    
                    yield Button("Next", id="next-button", variant="primary")
            with TabPane("Making SwiftOS yours.", disabled=True, classes="container") as pane:
                if initial == "tab-3" or initial == "tab-4":
                    pane.disabled = False
                
                yield MarkdownViewer(self.PAGES[2], id="info")
                
                with ScrollableContainer(id="setup-form"):
                    yield Static("[bold]Select a Background[/bold]", classes="center")
                    
                    width = console_bounds().columns
                    scale = int(width * 0.114942529)
                    
                    with Grid(id="image-grid"):
                        for image in get_backgrounds():
                            with Container(classes="image-container"):
                                yield Image(image, (scale, scale), id="image")
                                
                                image_text = os.path.basename(image)[:20][:-4]
                                if len(image_text) == 20:
                                    image_text += "..."
                                
                                yield Static(f"[blue]{image_text}[/blue]", id="image-path")
                                yield Button("Select", variant="success", id="select-background")
                                
                    yield Static("[bold]Select a Theme[/bold]", classes="center")
                    with Grid(id="theme-grid"):
                        with Container(classes="image-container"):
                            yield Static(f"[blue]Light[/blue]", id="image-path")
                            yield Button("Select", variant="success", id="select-light-theme")
                        with Container(classes="image-container"):
                            yield Static(f"[blue]Dark[/blue]", id="image-path")
                            yield Button("Select", variant="success", id="select-dark-theme")
                    
                    yield Button("Next", id="next-button", variant="primary")
            with TabPane("All done!", disabled=True, classes="container") as pane:
                if initial == "tab-4":
                    pane.disabled = False
                
                yield MarkdownViewer(self.PAGES[3], id="info")
                
                with ScrollableContainer(id="setup-form"):
                    yield Button("Finish", id="finish-button", variant="primary")
        
        """yield Tabs(
            Tab("Welcome!", disabled=False),
            Tab("Creating your account.", disabled=True),
            Tab("Making SwiftOS yours.", disabled=True),
            Tab("All done!", disabled=True)
        )
        
        with Container(id="container"):
            yield Markdown(self.PAGES[0], id="info")
            yield ScrollableContainer(id="setup-form")
        """