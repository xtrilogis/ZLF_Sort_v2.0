from assethandling.basemodels import UtilTabInput
from ui import Worker

ROOT = "../TestDateien"
ROOT_absolute = "D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien"
path = "D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien/Rohmaterial"
pfad_excel = "D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien/Rohmaterial/Zeltlagerfilm 2022.xlsx"

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


def bla():
    worker = Worker(function=get_util_input())
    worker.run()


if __name__ == "__main__":
    bla()
    # create_folder_structure()
    # process_raw()
    # process_util(get_util_input())
    print("")
    # print(fill_excel(Path("D:/Users/Wisdom/Lernen/Coding_Python/TestDateien/Zeltlagerfilm 2022.xlsx"),
    #                  Path("D:/Users/Wisdom/Lernen/Coding_Python/TestDateien/")))
