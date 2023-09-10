from datetime import datetime
from typing import List
from pathlib import Path

from assethandling.asset_manager import settings
from excel.excelmethods import create_emtpy_excel
from inputhandling import validation
from rawmaterial import raw_material
from assethandling.basemodels import ExcelOptions, FolderTabInput, UtilTabInput, RawTabStandardInput, SheetConfig
from ui import thread_worker as tw

ROOT = "../TestDateien"
ROOT_absolute = "D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien"
path = "D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien/Rohmaterial"
pfad_excel = "D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien/Rohmaterial/Zeltlagerfilm 2022.xlsx"


def create_folder_structure():
    worker = tw.Worker()
    data = FolderTabInput(
        folder=Path(ROOT_absolute),
        date=datetime.now()
    )
    worker.setup_folder_structure(inputs=data)


def get_raw_input():
    root = Path(ROOT_absolute)
    data = {
        "do_structure": False,
        "do_rename": False,
        "fill_excel": False,
        "create_picture_folder": False,
        "raw_material_folder": root / "Rohmaterial",  # TODO good??
        "first_folder_date": datetime(2023, 7, 26),
        "excel_option": ExcelOptions.EXISTING,
        "video_columns": settings["standard-video-columns"],
        "picture_columns": settings["standard-picture-columns"],
        "excel_file_name": f"Zeltlagerfilm {datetime.now().date().year}.xlsx",
        "excel_folder": root,
        "excel_full_filepath": root / f"Zeltlagerfilm {datetime.now().date().year}.xlsx",
        "picture_folder": root
    }
    return RawTabStandardInput(**data)


def process_raw(inputs: RawTabStandardInput):
    wk = tw.Worker()
    try:
        validate_and_prepare(inputs=inputs) # TODO implementation
    except Exception as e:
        print(str(e))
        return
    print("Inputs validiert und Excel eingelesen.")

    if inputs.do_structure:
        try:
            result = raw_material.correct_file_structure(
                raw_material_folder=inputs.raw_material_folder,
                dst_folder=inputs.raw_material_folder.parent / "New",
                start=inputs.first_folder_date
            )
            print(result)
        except Exception as e:
            print(str(e))
    if inputs.do_rename:
        try:
            result = raw_material.run_rename(raw_material_folder=inputs.raw_material_folder)
            print(result)
        except Exception as e:
            print(str(e))
    if inputs.fill_excel:
        try:
            result = raw_material.fill_excel(excel=inputs.excel_full_filepath,
                                             raw_material_folder=inputs.raw_material_folder)
            print(result)
        except Exception as e:
            print(str(e))
    if inputs.create_picture_folder:
        try:
            result = raw_material.create_picture_folder(picture_folder=inputs.picture_folder,
                                                        raw_material_folder=inputs.raw_material_folder)
            print(result)
        except Exception as e:
            print(str(e))

    print("BlaBla: raw gesamt fertig")


def validate_and_prepare(inputs: RawTabStandardInput):
    # TODO clean up excel creation
    # check if all is validated
    # add in complete process
    # add gui connection
    errors = []
    if not inputs.raw_material_folder.exists():
        errors.append("Bitte einen validen Pfad zum Rohmaterial angeben.")

    if inputs.fill_excel:
        if inputs.excel_option == ExcelOptions.EXISTING:
            # check exists, check is empty
            # res = validate_excel_file(excel)  # Todo use
            pass
        else:
            # TODO cleaner
            create_excel(file_name=inputs.excel_config.excel_file_name,
                         path=inputs.excel_config.excel_folder,
                         option=inputs.excel_config.excel_option,
                         columns=[inputs.excel_config.video_columns, inputs.excel_config.picture_columns],
                         override=False)
            # set excel_full_path

    if inputs.create_picture_folder:
        if not inputs.picture_folder.exists():
            errors.append("Bitte einen validen Pfad für den Bilderordner angeben.")

    valid, errors = validation.validate_raw(inputs=inputs)  # TODO implement
    if not valid:
        raise ValueError('\n'.join(errors))
    return errors


def create_excel(file_name: str,
                 path: Path,
                 option=ExcelOptions.STANDARD,
                 columns=None,
                 override=False):
    try:
        if file_name is None or not isinstance(path, Path) or not path.exists():
            raise AttributeError("Incorrect Input.")

        print("Starte Excel erstellen.")
        if option == ExcelOptions.STANDARD:
            sheets: List[SheetConfig] = [SheetConfig(name="Videos", columns=settings["standard-video-columns"]),
                                         SheetConfig(name="Bilder", columns=settings["standard-picture-columns"])]
        elif option == ExcelOptions.MANUAL and columns is not None:
            sheets: List[SheetConfig] = [SheetConfig(name="Videos", columns=columns[0]),
                                         SheetConfig(name="Bilder", columns=columns[1])]
        else:
            print("Called Function with incorrect parameters. \n"
                                         "Don't call with EXISTING or forget columns for manual.")
            return
        create_emtpy_excel(file_name=file_name, folder=path, sheet_configs=sheets, override=override)
        print("Excel-Datei erfolgreich erstellt")
    except FileExistsError:
        print("execl exists")
    except Exception as e:
        print(e)


def get_util_input():
    data = {
        "raw_material_folder": path,
        "excel_full_filepath": pfad_excel,
        "do_sections": False,
        "do_video_sections": True,
        "do_picture_sections": True,
        "rating_section": 4,
        "do_selections": False,
        "videos_columns_selection": ["Outtakes"],
        "picture_columns_selection": ["Outtakes", "Webseite", "Fotowand"],
        "marker": "x",
        "do_search": False,
        "videos_columns_search": [],
        "picture_columns_search": ["Outtakes", "Webseite", "Fotowand"],
        "keywords": ["x"],
        "rating_search": 3,
        "create_picture_folder": False,
        "rating_pictures": 4,
    }
    return UtilTabInput(**data)


def process_util(inputs: UtilTabInput):
    wk = tw.Worker()
    try:
        sheets = wk._validate_and_prepare(raw_material_folder=inputs.raw_material_folder,
                                          excel_full_filepath=inputs.excel_full_filepath)
    except Exception as e:
        print(str(e))
        return
    print("Inputs validiert und Excel eingelesen.")

    if inputs.do_sections:
        try:
            wk._handle_section(sheets=sheets, inputs=inputs)
        except Exception as e:
            print(str(e))
    if inputs.do_selections:
        try:
            wk._handle_selection(sheets=sheets, inputs=inputs)
        except Exception as e:
            print(str(e))
    if inputs.do_search:
        try:
            wk._handle_search(sheets=sheets, inputs=inputs)
        except Exception as e:
            print(str(e))
    if inputs.create_picture_folder:
        try:
            wk._handle_picture_folder(sheets=sheets, inputs=inputs)
        except Exception as e:
            print(str(e))

    print("BlaBla: util gesamt fertig")


def stats():
    wk = tw.Worker()
    wk.run_statistics()


if __name__ == "__main__":
    # create_folder_structure()
    # process_raw()
    # process_util(get_util_input())
    print("")
    # print(fill_excel(Path("D:/Users/Wisdom/Lernen/Coding_Python/TestDateien/Zeltlagerfilm 2022.xlsx"),
    #                  Path("D:/Users/Wisdom/Lernen/Coding_Python/TestDateien/")))
