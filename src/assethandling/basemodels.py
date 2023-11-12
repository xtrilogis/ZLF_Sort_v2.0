from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List

from pydantic import BaseModel

from assethandling.asset_manager import settings


class FolderTabInput(BaseModel):
    folder: Path
    date: datetime


class SheetConfig(BaseModel):
    name: str
    columns: List[str]


class ExcelInputOptions(Enum):
    # TODO bessere Beschriftung
    STANDARD = "Standard"
    MANUAL = "Manuelle Einstellungen"
    EXISTING = "Vorhandene Excel-Datei"


class ExcelOption(Enum):
    EXISTING = "existing"
    CREATE = "create"


class ExcelInput(BaseModel):
    option: ExcelOption
    name: str = f"Zeltlagerfilm {datetime.now().date().year}.xlsx"
    folder: Path
    video_columns: List[str] = settings["standard-video-columns"]
    picture_columns: List[str] = settings["standard-picture-columns"]

    @property
    def full_path(self) -> Path:
        return self.folder / self.name


class ExcelConfig(BaseModel):
    excel_folder: Path
    excel_file_name: str = f"Zeltlagerfilm {datetime.now().date().year}.xlsx"
    sheets: List[SheetConfig]


class RawTabInput(BaseModel):
    do_structure: bool = False
    do_rename: bool = False
    fill_excel: bool = False
    create_picture_folder: bool = False
    raw_material_folder: Path
    first_folder_date: datetime
    excel: ExcelInput
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
