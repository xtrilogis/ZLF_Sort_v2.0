from datetime import datetime
from typing import List
from pathlib import Path

from assethandling.basemodels import ExcelOptions, FolderTabInput, UtilTabInput
from inputhandling import validation
from ui import thread_worker as tw
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


def process_raw():
    # TODO implementaiton
    pass


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


# Abgleichen mit thread worker
def process_util(inputs):
    # TODO handle problem in one part of the execution
    valid, errors = validation.validate_util_paths(inputs.raw_material_folder,
                                                   inputs.excel_full_filepath)

    if not valid:
        print(errors)
    else:
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
                if inputs.videos_columns_search and not video_df.empty:
                    result = eval.search_columns(df=video_df,
                                                 raw_path=inputs.raw_material_folder,
                                                 columns=inputs.videos_columns_search,
                                                 markers=inputs.keywords,
                                                 rating=inputs.rating_search)
                    print("Videosuche erstellt.")
                    [print(x) for x in result if x]
                if inputs.picture_columns_search and not picture_df.empty:
                    result = eval.search_columns(df=picture_df,
                                                 raw_path=inputs.raw_material_folder,
                                                 columns=inputs.picture_columns_search,
                                                 markers=inputs.keywords,
                                                 rating=inputs.rating_search)
                    print("Bildersuche erstellt.")
                    [print(x) for x in result if x]
            if inputs.create_picture_folder:
                result = eval.copy_pictures_with_rating(df=picture_df,
                                                        raw_path=inputs.raw_material_folder,
                                                        rating_limit=inputs.rating_pictures)
                print("Bilderordner erstellt.")
                [print(x) for x in result if x]
            print("BlaBla: util gesamt fertig")

        except (IndexError, KeyError) as e:
            print("Fehler beim Laden der Excel-Datei.")
        except ValueError as e:
            print(str(e))


if __name__ == "__main__":
    # create_folder_structure()
    # process_raw()
    process_util(get_util_input())
