from datetime import datetime
from typing import List
from pathlib import Path
from PyQt5.QtCore import QDate
from assethandling.basemodels import ExcelOptions, FolderTabInput, UtilTabInput
from assethandling.asset_manager import settings
from inputhandling import validation
from ui import thread_worker as tw
from assethandling import asset_manager
from util import util_methods as eval

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


def process_raw_full():
    pass


def create_excel_from_sug():
    pass


def create_standard_excel():
    pass


def process_raw():
    worker = tw.Worker()
    #process_raw_full()

    #worker.correct_file_structure(path="")  # TODO

    # ### Excel File
    # vorhandene Excel einfach übernehmen
    # create excel
    #create_excel_from_sug()  # TODO
    #create_standard_excel()  # TODO
    # path standard Rohmaterial.parent
    worker.create_excel(file_name="test", path=Path(ROOT), option=ExcelOptions.MANUAL)  # TODO

    #worker.fill_excel()  # TODO

    #worker.create_picture_folder()  # TODO


def get_util_input():
    data = {
        "raw_material_folder": path,
        "excel_full_filepath": pfad_excel,
        "do_sections": False,
        "do_video_sections": True,
        "do_picture_sections": True,
        "rating_section": 4,
        "do_selections": True,
        "videos_columns_selection": ["Outtakes"],
        "picture_columns_selection": ["Outtakes", "Webseite", "Fotowand"],
        "marker": "x",
        "do_search": False,
        "videos_columns_search": [],
        "picture_columns_search": [],
        "keywords": [],
        "rating_search": 3,
        "create_picture_folder": False,
        "rating_pictures": 4,
    }
    return UtilTabInput(**data)


def process_util(inputs):
    # TODO handle problem in one part of the execution
    # Validate logic
    valid, errors = validation.validate_util()  # TODO
    if valid:
        try:
            sheets = eval.prepare_dataframes(excel_file=inputs.excel_full_filepath,
                                             raw_path=inputs.raw_material_folder)
            video_df = sheets["Videos"]
            picture_df = sheets["Bilder"]

            print("Inputs validiert und Excel eingelesen.")

            if inputs.do_sections:
                if inputs.do_video_sections and not video_df.empty:
                    result = eval.copy_section(video_df, inputs.rating_section)
                    print("Videoabschnitte erstellt.")
                    [print(x) for x in result if x]
                if inputs.do_picture_sections and not picture_df.empty:
                    result = eval.copy_section(picture_df, inputs.rating_section)
                    print("Bilderabschnitte erstellt.")
                    [print(x) for x in result if x]
            if inputs.do_selections:
                if inputs.videos_columns_selection and not video_df.empty:
                    result = eval.copy_selections(df=video_df,
                                                  raw_path=inputs.raw_material_folder,
                                                  columns=inputs.videos_columns_selection,
                                                  marker=inputs.marker)
                    print("Videoselektionen erstellt.")
                    [print(x) for x in result if x]
                if inputs.picture_columns_selection and not picture_df.empty:
                    result = eval.copy_selections(df=picture_df,
                                                  raw_path=inputs.raw_material_folder,
                                                  columns=inputs.picture_columns_selection,
                                                  marker=inputs.marker)
                    print("Bilderselektionen erstellt.")
                    [print(x) for x in result if x]
            if inputs.do_search:
                pass
            if inputs.create_picture_folder:
                pass
            print("BlaBla: util gesamt fertig")

        except (IndexError, KeyError) as e:
            print("Fehler beim Laden der Excel-Datei.")
        except ValueError as e:
            print(str(e))
    else:
        print(errors)


if __name__ == "__main__":
    # create_folder_structure()
    # process_raw()
    process_util(get_util_input())
