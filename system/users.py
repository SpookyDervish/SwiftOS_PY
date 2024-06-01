import os
import json

from rich_pixels import Pixels
from hashlib import sha256


class UserDoesntExistError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(f"The user \"{args[0]}\" does not exist.")
        
class UserAlreadyExistsError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(f"The user \"{args[0]}\" already exists.")
        
class InvalidUserError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(f"\"{args[0]}\" is not a user.")


def get_backgrounds():
    backgrounds = []
    
    for path in os.listdir("system/assets/images/backgrounds"):
        backgrounds.append(os.path.join("system/assets/images/backgrounds/", path))
    
    return backgrounds

def get_user_icon(username: str) -> str: 
    if os.path.isdir(f"home/{username}"):
        if os.path.isfile(f"home/{username}/user.png"):
            return f"home/{username}/user.png"
        else:
            return "system/assets/images/user/default_user.png"
    else:
        raise UserDoesntExistError(username)

def get_user_background(username: str) -> str:
    user_details = get_user_details(username)
    background = user_details["desktop_background"]
    
    return background

def get_user_details(username: str):
    if os.path.isdir(f"home/{username}"):
        if os.path.isfile(f"home/{username}/user.json"):
            contents = open(f"home/{username}/user.json", "r")
            details = json.loads(contents.read())
            contents.close()
            
            return details
        else:
            raise InvalidUserError(username)
    else:
        raise UserDoesntExistError(username)

# TODO: Make an actual way to check if a user is valid
def is_user_valid(username: str):
    user_details = get_user_details(username)
    
    if user_details["ready"]:
        return True
    return False

def get_valid_users():
    users = os.listdir("home")
    actual_users = []
    
    for user in users:
        if is_user_valid(user):
            actual_users.append(user)
        
    return actual_users

def get_users():
    users = os.listdir("home")
    actual_users = []
    
    for user in users:
        actual_users.append(user)
        
    return actual_users

def user_exists(username: str):
    return username in get_users()

def create_user(username: str, password: str, admin: bool = False, background: str = "", theme: str = ""):
    if os.path.isdir(f"home/{username}"):
        raise UserAlreadyExistsError(username)
    
    user_dir = f"home/{username}"
    
    os.mkdir(user_dir)
    
    user_json = open(f"home/{username}/user.json", "x")
    json.dump(
        {
            "password_hash": sha256(password.encode()).hexdigest(),
            "isAdmin": admin,
            
            "desktop_background": background,
            "theme": theme,
            
            "ready": False,
            
            "defaultPrograms": {
                "txt": "system/apps/Notepad.py"
            }
        },
        
        user_json,
        indent=4
    )
    user_json.close()
    
    os.mkdir(f"{user_dir}/Desktop")
    os.mkdir(f"{user_dir}/Documents")
    os.mkdir(f"{user_dir}/Downloads")
    os.mkdir(f"{user_dir}/Videos")
    os.mkdir(f"{user_dir}/Pictures")
    os.mkdir(f"{user_dir}/Music")
    
    return True
    
def change_user(username: str, password: str | None = None, admin: bool | None = None, background: str | None = None, theme: str | None = None, ready: bool | None = None):
    user_details = get_user_details(username)
    
    if password != None:
        hashed_password = sha256(password.encode()).hexdigest()
        user_details["password_hash"] = hashed_password
    if admin != None:
        user_details["isAdmin"] = admin
    if background != None:
        user_details["desktop_background"] = background
    if theme != None:
        user_details["theme"] = theme
    if ready != None:
        user_details["ready"] = ready

    contents = json.dumps(user_details, indent=4)
    
    json_file = open(f"home/{username}/user.json", "w")
    json_file.write(contents)
    json_file.close()
    
    