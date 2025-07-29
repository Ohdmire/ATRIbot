from pathlib import Path
from io import BytesIO
from ATRIlib.Config import path_config

help_file_path = path_config.help_file_path

def get_help():
    with open(help_file_path, 'rb') as f:
        image_bytes = BytesIO(f.read())
    return image_bytes
