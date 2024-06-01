import os
import sys
import time

from textual import work
from textual.app import ComposeResult
from textual.widgets import Static, Footer

from configparser import ConfigParser

from system.gui import loading_screen
from system.gui import login_screen
from system.gui import setup_screen
from system.gui.custom_widgets.window import Window
from system.gui.desktop_screen import Desktop
from system.users import get_valid_users, get_user_details
from system import fs
from main import SwiftOS


def on_ready(desktop: Desktop) -> ComposeResult:
    pass

@work
async def boot(app : SwiftOS, ini_path: str):
    """
    Boot SwiftOS.
    
    ! This should not be ran more than once.
    """
    
    app.log("Booting SwiftOS..\n")
    app.log("Showing loading screen..")
    
    loading = loading_screen.LoadingScreen()
    app.push_screen(loading)
    
    app.log("Parsing config..")
    parser = ConfigParser()
    parser.read(ini_path)
    
    if not os.path.isdir("home"):
        app.log("`home` folder does not exist! Creating..")
        os.mkdir("home")
        
    if len(get_valid_users()) == 0:
        app.log("No users found! Showing setup screen..")

        setup = setup_screen.SetupScreen()
        await app.push_screen_wait(setup)
        
        app.log("Setup completed!")
        setup.remove()
        del setup
    
    
    """app.log("Showing login screen..")
    
    login = login_screen.LoginScreen()
    login_form = login_screen.LoginForm(login)
    
    app.pop_screen()
    app.push_screen(login)
    
    app.bell() # We're loaded!
    
    logged_in_user = await app.push_screen_wait(login_form)
    app.log(f"Login completed! Logged in user: \"{logged_in_user}\"")"""
    logged_in_user = "Nathaniel"
    
    user_details = get_user_details(logged_in_user)
    if user_details["theme"] == "light":
        app.dark = False
    else:
        app.dark = True
    
    app.log("Loading desktop..")
    desktop = Desktop(logged_in_user)
    desktop.on_ready = on_ready
    
    app.pop_screen()
    app.push_screen(desktop)

    app.log("Cleaning up..")
    
    #await login_form.remove()
    #await login.remove()
    await loading.remove()
    
    #del login_form
    #del login
    del loading
    