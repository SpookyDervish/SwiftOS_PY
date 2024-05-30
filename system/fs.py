import os


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
        
def get_file_icon(file_path: str):
    icons = {
        ".txt": "system/assets/images/icons/file/txt.png"
    }
    
    _, extension = os.path.splitext(file_path)
    try:
        return icons[extension]
    except KeyError:
        return icons[".txt"]