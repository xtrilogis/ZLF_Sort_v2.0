import json
import os
import sys
from pathlib import Path

asset_folder: str = "assets"


def resource_path(file: str) -> Path:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")
    if "src" in base_path:
        # for starting the applications from gui_main.py without problems
        base_path = base_path.replace("src", "")
    if "tests" in base_path:
        # for starting the applications from gui_main.py without problems
        base_path = base_path.replace("tests", "")
    return Path(base_path) / asset_folder / file


def load_settings() -> dict:
    with open(resource_path("settings.json")) as file:
        return json.load(file)


settings: dict = load_settings()
window_icon = str(resource_path("window_icon.png"))
folder_icon = str(resource_path("folder-icon.png"))
gif = str(resource_path("output-onlinegiftools.gif"))
