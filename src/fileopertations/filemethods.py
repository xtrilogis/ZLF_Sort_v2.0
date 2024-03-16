import filecmp
import shutil
from datetime import datetime
from os.path import getmtime
from pathlib import Path
from typing import List, Optional

import PIL.Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

from assethandling import constants
from assethandling.basemodels import File, FileType


def create_folder(parent: Path, folder: str) -> Path:
    create: Path = parent.joinpath(folder)
    if not create.exists():
        create.mkdir(parents=True)
    return create


def copy_file(src_file: Path, dst_folder: Path):
    """
    copy the given file to the given folder
    Note: if a file with the same name already exists
    the file will be renamed to filename(nr), nr will be increased until the name doesn't exist
    """
    # feat: make overwrite possible/optional
    if not dst_folder.exists():
        dst_folder.mkdir(parents=True)
    file_dst: Path = dst_folder / src_file.name
    counter = 1
    while file_dst.exists():
        if filecmp.cmp(src_file, file_dst):
            return
        file_dst: Path = dst_folder / f"{src_file.stem}({counter}){src_file.suffix}"
        counter += 1
    shutil.copy(src=src_file, dst=file_dst)


def rename_files(folder: Path, all_files: List[File], progress_callback):
    renamed_files_nr: int = 0
    length = 3 if len(all_files) < 999 else 4

    special_folder = (
        "sonstiges" in folder.parent.name.lower()
        or "sonstiges" in folder.parent.parent.name.lower()
    )
    for index, file in enumerate(all_files):
        try:
            name = "Sonstiges" if special_folder else file.date.strftime("%m_%d_%a")
            new_filepath = file.full_path.with_name(
                name=f"{name}-{format(index + 1).zfill(length)}{file.full_path.suffix}"
            )
            file.full_path.rename(new_filepath)
            renamed_files_nr += 0
        except (FileNotFoundError, FileExistsError, WindowsError) as e:
            progress_callback.emit(
                f"Datei {file.full_path.name} wurde nicht umbenannt\n- Fehler: {type(e).__name__}"
            )
    progress_callback.emit(f"{renamed_files_nr} Dateien umbenannt.")


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
            captured_date: datetime = datetime.fromtimestamp(getmtime(str(file)))
        return captured_date


def _get_image_captured_date(file: Path) -> Optional[datetime]:
    captured_date: Optional[datetime] = None

    with PIL.Image.open(file) as image:
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
    with createParser(str(file)) as parser:
        metadata = extractMetadata(parser)
        if metadata:
            for line in metadata.exportPlaintext():
                if "Creation date" in line:
                    result = line.split(": ")[1].strip()
                    captured_date: datetime = datetime.fromisoformat(result)

    return captured_date
