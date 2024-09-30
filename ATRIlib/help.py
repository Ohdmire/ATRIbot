from pathlib import Path
from io import BytesIO

help_file_path = Path('./assets/help/help.png')

def get_help():
    with open(help_file_path, 'rb') as f:
        image_bytes = BytesIO(f.read())
    return image_bytes
