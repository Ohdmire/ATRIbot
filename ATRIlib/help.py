import json
import os
from io import BytesIO

from ATRIlib.Config import path_config
from ATRIlib.DRAW.draw_help import draw_help

_help_cache = {"key": None, "data": None}


def _cache_key():
    return (
        os.path.getmtime(path_config.help_json_file_path),
        os.path.getmtime(path_config.help_template_file_path),
        os.path.getmtime(path_config.help_atri_file_path),
    )


def get_help():
    key = _cache_key()
    if _help_cache["data"] is not None and _help_cache["key"] == key:
        return BytesIO(_help_cache["data"])

    with open(path_config.help_json_file_path, "r", encoding="utf-8") as f:
        help_data = json.load(f)

    image = draw_help(help_data)
    data = image.getvalue()

    _help_cache["key"] = key
    _help_cache["data"] = data
    return BytesIO(data)
