from pathlib import Path

from inputhandling.validation import is_valid_folder, validate_excel_file
from rawmaterial import raw_material as raw


def handle_create_excel():
    pass


def handle_fill_excel(excel: Path, raw_material_folder: Path):
    errors = validate_excel_file(excel)
    if errors:
        errors.insert(0, "Dateien in Excel schreiben.")
        raise ValueError('\n'.join(errors))
    return raw.fill_excel(excel=excel, raw_material_folder=raw_material_folder)


def handle_create_picture_folder(raw_material_folder, folder: Path):
    folder.mkdir()
    if not is_valid_folder(folder):
        raise ValueError("Bitte gib einen gültigen Zielordner an.")

    return raw.create_picture_folder(picture_folder=folder,
                                     raw_material_folder=raw_material_folder)
