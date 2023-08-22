from enum import Enum
from typing import List

from pydantic import BaseModel


class SheetConfig(BaseModel):
    name: str
    columns: List[str]


class ExcelOptions(Enum):
    # TODO bessere Beschriftung
    STANDARD = "Standard"
    MANUAL = "Spalten Manuell"
    EXISTING = "Vorhandene Excel-Datei"
