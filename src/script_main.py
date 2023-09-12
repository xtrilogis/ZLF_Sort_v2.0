from datetime import datetime
from typing import List
from pathlib import Path

from assethandling.asset_manager import settings
from excel.excelmethods import create_emtpy_excel
from inputhandling import validation
from rawmaterial import raw_material
from assethandling.basemodels import ExcelOptions, FolderTabInput, UtilTabInput, RawTabInput, SheetConfig, \
    ExcelConfig, ExcelInput
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


# def get_raw_input():
#     root = Path(ROOT_absolute)
#     input_ = ExcelInput(
#         excel_folder=root,
#         # video_columns=settings["standard-video-columns"],
#         # picture_columns=settings["standard-picture-columns"],
#         # excel_file_name=f"Zeltlagerfilm {datetime.now().date().year}.xlsx",
#     )
#     data = {
#         "do_structure": False,
#         "do_rename": False,
#         "fill_excel": False,
#         "create_picture_folder": False,
#         "raw_material_folder": root / "Rohmaterial",  # TODO good??
#         "first_folder_date": datetime(2023, 7, 26),
#         "excel_full_filepath": root / f"Zeltlagerfilm {datetime.now().date().year}.xlsx",
#         "picture_folder": root
#     }
#     return RawTabInput(**data)
#
#
# def process_raw(inputs: RawTabInput):
#     wk = tw.Worker()
#     try:
#         validate_and_prepare(inputs=inputs)  # TODO implementation
#     except Exception as e:
#         print(str(e))
#         return
#     print("Inputs validiert und Excel eingelesen.")
#
#     if inputs.do_structure:
#         try:
#             result = raw_material.correct_file_structure(
#                 raw_material_folder=inputs.raw_material_folder,
#                 dst_folder=inputs.raw_material_folder.parent / "New",
#                 start=inputs.first_folder_date
#             )
#             print(result)
#         except Exception as e:
#             print(str(e))
#     if inputs.do_rename:
#         try:
#             result = raw_material.run_rename(raw_material_folder=inputs.raw_material_folder)
#             print(result)
#         except Exception as e:
#             print(str(e))
#     if inputs.fill_excel:
#         try:
#             result = raw_material.fill_excel(excel=inputs.excel_config.excel_full_filepath,
#                                              raw_material_folder=inputs.raw_material_folder)
#             print(result)
#         except Exception as e:
#             print(str(e))
#     if inputs.create_picture_folder:
#         try:
#             result = raw_material.create_picture_folder(picture_folder=inputs.picture_folder,
#                                                         raw_material_folder=inputs.raw_material_folder)
#             print(result)
#         except Exception as e:
#             print(str(e))
#
#     print("BlaBla: raw gesamt fertig")

def create_excel(input_: ExcelInput, override=False) -> Path:
    config = ExcelConfig(
        excel_folder=input_.excel_folder,
        excel_file_name=input_.excel_file_name,
        sheets=[SheetConfig(name="Videos", columns=input_.video_columns),
                SheetConfig(name="Bilder", columns=input_.picture_columns)]
    )
    return create_emtpy_excel(config=config, override=override)


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
