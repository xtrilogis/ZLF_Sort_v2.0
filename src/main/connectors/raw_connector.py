from pathlib import Path

from assethandling.basemodels import ExcelInput, ExcelConfig, SheetConfig
from assets import constants
from excel.excelmethods import create_emtpy_excel
from inputhandling.validation import is_valid_folder, validate_excel_file
from rawmaterial import raw_material as raw


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


def handle_create_excel(config: ExcelInput, get_data):
    vid = constants.minimal_columns.copy()
    vid.extend(config.video_columns)
    pic = constants.minimal_columns.copy()
    pic.extend(config.picture_columns)
    config = ExcelConfig(
        excel_folder=config.excel_folder,
        excel_file_name=config.excel_file_name,
        sheets=[SheetConfig(name="Videos", columns=vid),
                SheetConfig(name="Bilder", columns=pic)]
    )
    try:
        path = create_emtpy_excel(config=config)
    except FileExistsError:
        # todo
        override: str = get_data(text="Excel existiert bereits. Soll sie überschrieben werden? j/n")
        res = override.lower() == "j"
        path = create_emtpy_excel(config=config, override=res)
    return path
