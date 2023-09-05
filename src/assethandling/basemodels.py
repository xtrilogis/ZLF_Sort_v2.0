from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List

from pydantic import BaseModel

from assethandling.asset_manager import settings


class SheetConfig(BaseModel):
    name: str
    columns: List[str]


class ExcelOptions(Enum):
    # TODO bessere Beschriftung
    STANDARD = "Standard"
    MANUAL = "Manuelle Einstellungen"
    EXISTING = "Vorhandene Excel-Datei"


class FolderTabInput(BaseModel):
    folder: Path
    date: datetime


class ExcelConfig(BaseModel):
    excel_option: ExcelOptions
    video_columns: List[str] = settings["standard-video-columns"]
    picture_columns: List[str] = settings["standard-picture-columns"]
    excel_file_name: str = f"Zeltlagerfilm {datetime.now().date().year}.xlsx"
    excel_folder: Path | None
    excel_full_filepath: Path | None


class RawTabStandardInput(BaseModel):
    do_structure: bool
    do_rename: bool
    fill_excel: bool
    create_picture_folder: bool
    raw_material_folder: Path
    first_folder_date: datetime
    excel_config: ExcelConfig
    picture_folder: Path


class UtilTabInput(BaseModel):
    raw_material_folder: Path
    excel_full_filepath: Path
    do_sections: bool
    do_video_sections: bool
    do_picture_sections: bool
    rating_section: int
    do_selections: bool
    videos_columns_selection: List[str]
    picture_columns_selection: List[str]
    marker: str
    do_search: bool
    videos_columns_search: List[str]
    picture_columns_search: List[str]
    keywords: List[str]
    rating_search: int
    create_picture_folder: bool
    rating_pictures: int


class FileType(Enum):
    VIDEO = "Video"
    IMAGE = "Image"
    OTHER = "other"


class File(BaseModel):
    full_path: Path
    date: datetime
    dst_folder: Path | None
    type: FileType
