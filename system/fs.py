import os

import imp

from system.users import get_user_details


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
        "txt": "system/assets/images/icons/file/txt.png"
    }
    
    extension = get_file_extension(file_path)
    try:
        return icons[extension]
    except KeyError:
        return icons[".txt"]
    
def run(app_path: str, desktop, args: list[str]):
    name = os.path.basename(app_path)[:-3]
    path = os.path.abspath(app_path)

    app = imp.load_source(name, path)
    
    return app.execute(desktop, args)
    
def open_file(file_path: str, desktop):
    if os.path.isdir(file_path):
        raise IsADirectoryError(file_path)
    
    if not os.path.isfile(file_path): # The file doesn't exist
        raise FileNotFoundError(file_path)
    
    current_user = desktop.logged_in_user
    
    user_details = get_user_details(current_user)
    apps = user_details["defaultPrograms"]
    
    ext = get_file_extension(file_path)
    try:
        default_app = apps[ext]
    except KeyError: # There is no default app to handle this file extension...
        return get_file_extension(file_path)
    
    return run(default_app, desktop, [file_path])