import filecmp
import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

import PIL.Image
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

from assethandling.basemodels import FileType
from assets import constants


def copy_file(src_file: Path, dst_folder: Path):
    if not dst_folder.exists():
        dst_folder.mkdir(parents=True)
    file_dst: Path = dst_folder / src_file.name
    counter = 1
    while file_dst.exists():
        if filecmp.cmp(src_file, file_dst):
            return
        file_dst: Path = dst_folder / f'{src_file.stem}({counter}){src_file.suffix}'
        counter += 1
    shutil.copy(src=src_file, dst=file_dst)
    # return new location


def get_file_type(file: Path) -> FileType:
    if file.suffix.upper() in constants.video_extensions:
        return FileType.VIDEO
    if file.suffix.upper() in constants.image_extensions:
        return FileType.IMAGE
    return FileType.OTHER


# Maybe own file for date operations
def get_file_captured_date(file: Path, file_type) -> datetime:
    captured_date: Optional[datetime] = None
    try:
        if file_type == FileType.IMAGE:
            captured_date: Optional[datetime] = _get_image_captured_date(file)
        if file_type == FileType.VIDEO:
            captured_date: Optional[datetime] = _get_video_captured_date(file)
    finally:
        if captured_date is None:
            captured_date: datetime = datetime.fromtimestamp(os.path.getmtime(str(file)))
        return captured_date


def _get_image_captured_date(file: Path) -> Optional[datetime]:
    captured_date: Optional[datetime] = None

    image = PIL.Image.open(file)
    exif_data = image._getexif()
    for tag, value in exif_data.items():
        tag_name = PIL.ExifTags.TAGS.get(tag, tag)
        if tag_name == "DateTimeOriginal" or tag_name == "DateTime":
            extracted_date: datetime = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
            if captured_date is None or extracted_date < captured_date:
                captured_date = extracted_date

    return captured_date


def _get_video_captured_date(file: Path) -> Optional[datetime]:
    captured_date: Optional[datetime] = None

    parser = createParser(str(file))
    metadata = extractMetadata(parser)
    if metadata:
        for line in metadata.exportPlaintext():
            if "Creation date" in line:
                result = line.split(": ")[1].strip()
                captured_date: datetime = datetime.fromisoformat(result)

    return captured_date
