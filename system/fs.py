import os

import imp

from system.users import get_user_details
from system.gui.custom_widgets.dialog import create_dialog, DialogIcon


def find_file(file_name: str, dir: str = None):
    """Recursively search for a file in a directory.

    Args:
        file_name (str): The file being searched for.
        dir (str, optional): The directory to search inside of. Defaults to the current working directory.

    Returns:
        str?: Returns the path the file if it was found, otherwise returns `None`.
    """
    
    for root, _, files in os.walk(dir):
        if file_name in files:
            return os.path.join(root, file_name)
        
def get_file_extension(file_path: str):
    _, extension = os.path.splitext(file_path)
    return extension[1:]
        
def get_file_icon(file_path: str):
    icons = {
        "txt": "system/assets/images/icons/file/txt.png",
        "/folder\\": "system/assets/images/icons/file/folder.png"
    }
    
    extension = get_file_extension(file_path)
    try:
        return icons[extension]
    except KeyError:
        if not os.path.isdir(file_path):
            return icons["txt"]
        else:
            return icons["/folder\\"]
    
def run(app_path: str, desktop, args: list[str]):
    name = os.path.basename(app_path)[:-3]
    path = os.path.abspath(app_path)

    try:
        app = imp.load_source(name, path)
    except FileNotFoundError: # Couldn't run the app because it doesn't exist
        create_dialog(
            f"The system cannot find the specified file:\n[blue]{app_path}[/blue]",
            desktop,
            "SwiftOS error",
            icon=DialogIcon.EXCLAMATION
        )
        return 1
    
    return app.execute(desktop, args)
    
def open_file(file_path: str, desktop):    
    current_user = desktop.logged_in_user
    
    user_details = get_user_details(current_user)
    apps = user_details["defaultPrograms"]
    
    ext = get_file_extension(file_path)
    
    if os.path.isdir(file_path):
        ext = "/folder\\"
    
    if not os.path.exists(file_path): # The file doesn't exist
        raise FileNotFoundError(file_path)
    
    try:
        default_app = apps[ext]
    except KeyError: # There is no default app to handle this file extension...
        create_dialog(
            "There is no default app to handle this kind of file. Support for changing default apps will be coming in a future release of SwiftOS. We apolagize for the inconvenicence.",
            desktop,
            "SwiftOS Error",
            icon=DialogIcon.EXCLAMATION
        )
        return False
    
    return run(default_app, desktop, [file_path])