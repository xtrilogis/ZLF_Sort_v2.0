import datetime
import filecmp
import locale
import os
import shutil
import time
from datetime import date
from pathlib import Path

import pandas as pd
import PIL.Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pydantic import BaseModel

from assethandling import constants
from excel import excelmethods
from fileopertations.filemethods import copy_file

name = 97  # kleines a in ascii
# print(chr(name+1))

file = "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/Level1/Soll/Schnittmaterial/25-07-Do_1.MTS"
path = "D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien/Rohmaterial - nach Nachschauen"
pfad_excel = "D:/Users/Wisdom/Lernen/Coding_Python/ZLF_Sort_v2.0/TestDateien/Rohmaterial - nach Nachschauen/Zeltlagerfilm 2023.xlsx"


def get_image_date_properties(file):
    img = PIL.Image.open(file)
    exif_data = img._getexif()
    # print(file.name)
    # print(exif_data)
    try:
        img = PIL.Image.open(file)
        exif_data = img._getexif()

        for tag, value in exif_data.items():
            tag_name = PIL.ExifTags.TAGS.get(tag, tag)
            # print(tag_name, value)
            if tag_name == "DateTimeOriginal" or tag_name == "DateTime":
                print(datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S"))
        # print("...")
        # for tag, value in img.getexif().items():
        #     tag_name = PIL.ExifTags.TAGS.get(tag, tag)
        #     print(tag_name, value)
    except (AttributeError, KeyError, IndexError) as e:
        print(e)
        pass
    ti_c = os.path.getctime(file)  # Creation time
    ti_m = os.path.getmtime(file)  # Änderungsdatum
    ti_a = os.path.getatime(file)
    print(
        "ctime = Erstelldatum "
        + time.strftime("%m-%d", time.strptime(time.ctime(ti_c)))
    )
    print(
        "mtime = Änderungsdatum "
        + time.strftime("%m-%d", time.strptime(time.ctime(ti_m)))
    )
    print(
        "atime = letzter Zugriff o.s."
        + time.strftime("%m-%d", time.strptime(time.ctime(ti_a)))
    )


# general files
def format_date(file):
    ti_c = os.path.getctime(file)  # Creation time
    ti_m = os.path.getmtime(file)  # Änderungsdatum
    ti_a = os.path.getatime(file)
    print(ti_m)
    c_ti = time.ctime(ti_c)
    print(c_ti)
    m_ti = time.ctime(ti_m)
    a_ti = time.ctime(ti_a)
    # print(m_ti[:3])

    # tim = time.strptime(m_ti) # Datum zum formatieren bereit machen
    t_s2 = time.strftime("%m-%d", time.strptime(c_ti))
    t_s = time.strftime("%m-%d", time.strptime(m_ti))
    t_s4 = time.strftime("%m-%d", time.strptime(a_ti))  # Datum formatieren
    print(t_s, t_s2, t_s4)


def get_video_date_properties(file):
    parser = createParser(file)
    metadata = extractMetadata(parser)

    if metadata:
        print(metadata)
        for line in metadata.exportPlaintext():
            # print(line)
            if "Creation date" in line:
                result = line.split(":")[1].strip()
                # print(result)

    ti_c = os.path.getctime(file)  # Creation time
    ti_m = os.path.getmtime(file)  # Änderungsdatum
    ti_a = os.path.getatime(file)
    print("ctime = Erstelldatum " + time.ctime(ti_c))
    print("mtime = Änderungsdatum " + time.ctime(ti_m))
    print("atime = letzter Zugriff o.s." + time.ctime(ti_a))
    return None


def write_excel_without_delete(pfad_excel):
    df_videos = pd.read_excel(pfad_excel, sheet_name="Videos")
    print(df_videos)
    df_videos.loc[2, "Datei"] = "test"
    print(df_videos)
    with pd.ExcelWriter(pfad_excel) as writer:  # doctest: +SKIP
        df_videos.to_excel(writer, index=False, sheet_name="Videos")


def try_os_join():
    path_ziel = (
        "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/Level2/Schnittmaterial/"
    )
    file = "07-25-Do_001.MTS"
    root = "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/Level2/Rohmaterial/a Do 25.07"
    root2 = "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/Level2/Rohmaterial/a Do 25.07/"
    root3 = "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/Level2/Rohmaterial/a Do 25.07//"
    full_file_path1 = os.path.join(root, file)
    full_file_path2 = os.path.join(root2, file)
    full_file_path3 = os.path.join(root3, file)
    try:
        shutil.copy(full_file_path1, path_ziel + file)
        print(f"Successfully copied 1")
    except FileNotFoundError:
        print(f"Error File not found 1")
    try:
        shutil.copy(full_file_path2, path_ziel + file)
        print(f"Successfully copied 2")
    except FileNotFoundError:
        print(f"Error File not found 2")
    try:
        shutil.copy(full_file_path3, path_ziel + file)
        print(f"Successfully copied 3")
    except FileNotFoundError:
        print(f"Error File not found 3")


def convert_string_to_list(videos: str, pictures: str):
    videos_columns = videos.split(",")
    pic_columns = pictures.split(",")
    return videos_columns, pic_columns


def save_excel():
    """Saves Pandas DataFrames to Excel"""
    excel = "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/Basic Tests/tag_pic_vid/Rohmaterial - Kopie/Zeltlagerfilm 2022.xlsx"
    # Lösung, wenn Excel nicht schreibbar
    # writer = pd.ExcelWriter(self.excel, engine='xlsxwriter')
    df1 = pd.DataFrame(
        [["a", "b"], ["c", "d"]], index=["row 1", "row 2"], columns=["col 1", "col 2"]
    )
    df1.to_excel(excel, index=False, sheet_name="Videos")
    # self.df_pictures.to_excel(excel, index=False, sheet_name='Bilder')
    # writer.save()


def load_excel():
    result = pd.read_excel(pfad_excel)
    print("")


def get_column_list(columns: str):  # -> List[str]:
    cols = []
    for part in columns.split(","):
        if part.strip():
            cols.append(part.strip())
    return cols


def os_walk(sheets):
    sheets["Videos"]["Dateipfad"] = pd.Series(dtype="str")
    sheets["Bilder"]["Dateipfad"] = pd.Series(dtype="str")
    for element in Path(path).glob("**/*"):
        if element.is_file():
            if element.suffix.upper() in constants.video_extensions:
                df = sheets["Videos"]
            elif element.suffix.upper() in constants.image_extensions:
                df = sheets["Bilder"]
            else:
                continue
            match = df.loc[df["Datei"] == element.name]
            if not match.empty:
                row = match.index[0]
                df.loc[row, "Dateipfad"] = element


def some_fn(input, bla):
    for i in input:
        print(i)
    print(bla)


def run(function, titel, **kwargs):
    function(**kwargs)
    print(titel)
    pass


class Mai(BaseModel):
    eigenschaft: str


class Sdf(Mai):
    some_value: str


class ExcelInput(BaseModel):
    # option: ExcelOption
    name: str = f"Zeltlagerfilm"  # {datetime.now().date().year}.xlsx"
    folder: Path
    # full_path: Path
    # video_columns: List[str] = settings["standard-video-columns"]
    # picture_columns: List[str] = settings["standard-picture-columns"]

    @property
    def full_path(self) -> Path:
        return self.folder / self.name


def func1(name, age):
    func2(name=name, age=age)


def func2(name, **kwargs):
    print(name)


if __name__ == "__main__":
    # run(some_fn, titel="sfda", bla="asdf", input=[1, 2, 4])
    # nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    # res = ExcelInput(folder=Path("test/path"))
    # print(res.full_path)
    func1("tom", 23)
    pass
