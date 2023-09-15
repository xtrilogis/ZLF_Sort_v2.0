import json
from pathlib import Path

ROOT: Path = Path(__file__).parent.parent.parent
asset_folder: Path = ROOT / "assets"


def asset_path(file: str) -> Path:
    return asset_folder / file


def load_settings() -> dict:
    with open(asset_path("settings.json")) as file:
        return json.load(file)


settings: dict = load_settings()
# excel_Datei = "../assets/Zeltlagerfilm 2023.xlsx"
window_icon: Path = asset_path("window_icon.png")
