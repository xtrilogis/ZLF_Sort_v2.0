import os
from enum import Enum
from pathlib import Path
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict

from pydantic import BaseModel, ValidationError
import PIL.Image
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from assets import constants
from fileopertations import filemethods
from foldersetup import folder_setup


class FileType(Enum):
    VIDEO = "Video"
    IMAGE = "Image"
    OTHER = "other"


class File(BaseModel):
    full_path: Path
    date: datetime
    dst_folder: Path | None
    type: FileType


def correct_file_structure(raw_material_folder: Path, dst_folder: Path, start: datetime):
    errors = []
    check_if_right_structure()
    # sort into day folders, sort into Bilder, Videos
    # alles vor date und alles nach date + 10 in Sonstiges
    all_files: List[File] = []
    for element in raw_material_folder.glob('**/*'):
        if element.is_file():
            file_type = get_file_type(element)
            if file_type != FileType.IMAGE and file_type != FileType.VIDEO:
                continue
            datum = get_file_captured_date(element, file_type)

            try:
                all_files.append(File(full_path=element, date=datum, dst_folder=None, type=file_type))
            except ValidationError as e:
                errors.append(f"Datei {element.name}: {str(e)}")

    # all_files.sort(key=lambda x: x.date, reverse=False)
    # day_folders = folder_setup.day_folder(date)
    structure: Dict[str | date, Dict[str, List[File]]] = {}

    for i in range(10):
        structure[start.date()]: Dict[str, List[File]] = {FileType.VIDEO.value: [], FileType.IMAGE.value: []}
        start += timedelta(days=1)
    structure["Sonstiges"]: Dict[str, List[File]] = {FileType.VIDEO.value: [], FileType.IMAGE.value: []}

    for file in all_files:
        if file.date.date() in structure.keys():
            structure[file.date.date()][file.type.value].append(file)
        else:
            structure["Sonstiges"][file.type.value].append(file)

    letter = 97
    for key, value in structure.items():
        if isinstance(key, date):
            folder = dst_folder / f'{chr(letter)}-{key.strftime("%d.%m")}-{key.strftime("%A")}'
            for element in value[FileType.VIDEO.value]:
                filemethods.copy_file(element.full_path, folder / "Videos")

            for element in value[FileType.IMAGE.value]:
                filemethods.copy_file(element.full_path, folder / "Bilder")
        else:
            folder = dst_folder / f'{chr(letter)}-{"Sonstiges"}'
            for element in value[FileType.VIDEO.value]:
                filemethods.copy_file(element.full_path, folder / "Videos")

            for element in value[FileType.IMAGE.value]:
                filemethods.copy_file(element.full_path, folder / "Bilder")
        letter += 1

    return errors


def get_file_captured_date(file: Path, file_type) -> datetime:
    captured_date = None
    try:
        if file_type == FileType.IMAGE:
            captured_date = _get_image_captured_date(file)
        if file_type == FileType.VIDEO:
            captured_date = _get_video_captured_date(file)
    finally:
        if captured_date is None:
            captured_date = datetime.fromtimestamp(os.path.getmtime(str(file)))
        return captured_date


def _get_image_captured_date(file: Path) -> Optional[datetime]:
    captured_date: Optional[datetime] = None

    image = PIL.Image.open(file)
    exif_data = image._getexif()
    for tag, value in exif_data.items():
        tag_name = PIL.ExifTags.TAGS.get(tag, tag)
        if tag_name == "DateTimeOriginal" or tag_name == "DateTime":
            date = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
            if captured_date is None or date < captured_date:
                captured_date = date

    return captured_date


def _get_video_captured_date(file: Path) -> Optional[datetime]:
    captured_date: Optional[datetime] = None

    parser = createParser(str(file))
    metadata = extractMetadata(parser)
    if metadata:
        for line in metadata.exportPlaintext():
            if "Creation date" in line:
                result = line.split(": ")[1].strip()
                captured_date = datetime.fromisoformat(result)

    return captured_date


def get_file_type(file: Path) -> FileType:
    if file.suffix in constants.video_extensions:
        return FileType.VIDEO
    if file.suffix in constants.image_extensions:
        return FileType.IMAGE
    return FileType.OTHER


def check_if_right_structure():
    pass


if __name__ == "__main__":
    path = Path("D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien/Rohmaterial/") # "D:/Users/Wisdom/Allgemein/PJHF/2022_23/Zeltlager/Zeltlagerfilm/Rohmaterial/Sonstiges/Videos/")
    
    # test_file = path / "07-26-Mi_001.JPG" # 08-05-Sa_153.jpg, 08-05-Sa_071.jpeg, 08-05-Sa_081.jpg
    correct_file_structure(path, Path("D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien/"), datetime(2022, 7, 27))
