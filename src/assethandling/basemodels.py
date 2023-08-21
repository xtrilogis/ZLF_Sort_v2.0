from typing import List

from pydantic import BaseModel


class SheetConfig(BaseModel):
    name: str
    columns: List[str]
