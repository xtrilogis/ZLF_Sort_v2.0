import datetime
import locale
import os
from datetime import date
import time
from pathlib import Path

import pandas as pd
import shutil
import PIL.Image
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata



name = 97  # kleines a in ascii
# print(chr(name+1))

file = "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/Level1/Soll/Schnittmaterial/25-07-Do_1.MTS"
path = "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/Level1/Rohmaterial/07-25-Do_002.MOV"
pfad_excel = "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/Level1/Rohmaterial"


def read_file_extensions(path):
    """Prints all file extensions"""

    for root, _, files in os.walk(path):
        for f in files:
            filename, file_ext = os.path.splitext(f)
            print(file_ext)


def get_image_date_properties(file):
    img = PIL.Image.open(file)
    exif_data = img._getexif()
    print(exif_data)
    try:
        img = PIL.Image.open(file)
        exif_data = img._getexif()

        for tag, value in exif_data.items():
            tag_name = PIL.ExifTags.TAGS.get(tag, tag)
            if tag_name == "DateTimeOriginal":
                print(value)
    except (AttributeError, KeyError, IndexError):
        pass
    ti_c = os.path.getctime(file)  # Creation time
    ti_m = os.path.getmtime(file)  # Änderungsdatum
    ti_a = os.path.getatime(file)
    print("ctime = Erstelldatum " + time.strftime("%m-%d", time.strptime(time.ctime(ti_c))))
    print("mtime = Änderungsdatum " + time.strftime("%m-%d", time.strptime(time.ctime(ti_m))))
    print("atime = letzter Zugriff o.s." + time.strftime("%m-%d", time.strptime(time.ctime(ti_a))))

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
    t_s4 = time.strftime("%m-%d", time.strptime(a_ti))# Datum formatieren
    print(t_s, t_s2, t_s4)


def get_video_date_properties(file):
        parser = createParser(file)
        metadata = extractMetadata(parser)

        if metadata:
            print(metadata)
            for line in metadata.exportPlaintext():
                # print(line)
                if "Creation date" in line:
                    result =line.split(":")[1].strip()
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
    df_videos.loc[2, 'Datei'] = "test"
    print(df_videos)
    with pd.ExcelWriter(pfad_excel) as writer:  # doctest: +SKIP
        df_videos.to_excel(writer, index=False, sheet_name='Videos')


def try_os_join():
    path_ziel = "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/Level2/Schnittmaterial/"
    file = "07-25-Do_001.MTS"
    root = "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/Level2/Rohmaterial/a Do 25.07"
    root2 = "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/Level2/Rohmaterial/a Do 25.07/"
    root3 = "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/Level2/Rohmaterial/a Do 25.07\\"
    full_file_path1 = os.path.join(root, file)
    full_file_path2 = os.path.join(root2, file)
    full_file_path3 = os.path.join(root3, file)
    try:
        shutil.copy(full_file_path1, path_ziel + file)
        print(f'Successfully copied 1')
    except FileNotFoundError:
        print(f'Error File not found 1')
    try:
        shutil.copy(full_file_path2, path_ziel + file)
        print(f'Successfully copied 2')
    except FileNotFoundError:
        print(f'Error File not found 2')
    try:
        shutil.copy(full_file_path3, path_ziel + file)
        print(f'Successfully copied 3')
    except FileNotFoundError:
        print(f'Error File not found 3')


def convert_string_to_list(videos: str, pictures: str):
    videos_columns = videos.split(",")
    pic_columns = pictures.split(",")
    return videos_columns, pic_columns

def save_excel():
    """Saves Pandas DataFrames to Excel"""
    excel = "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/Basic Tests/tag_pic_vid/Rohmaterial - Kopie/Zeltlagerfilm 2022.xlsx"
    # Lösung, wenn Excel nicht schreibbar
    # writer = pd.ExcelWriter(self.excel, engine='xlsxwriter')
    df1 = pd.DataFrame([['a', 'b'], ['c', 'd']],

                       index=['row 1', 'row 2'],

                       columns=['col 1', 'col 2'])
    df1.to_excel(excel, index=False, sheet_name='Videos')
    #self.df_pictures.to_excel(excel, index=False, sheet_name='Bilder')
    #writer.save()


def get_parent_folder(path: str):
    for root, _, files in os.walk(path):
        print(files)

class Some:
    one: str = None

    def __init__(self):
        self.two: str = None

    def s(self):
        if not self.one:
            self.one = "sdf"

        if not self.two:
            self.two = "aes"

    def up(self):
        self.s()
        print(self.two)
        print(self.one)

def create(par, *folders):
    parent.joinpath(folders)


if __name__ == '__main__':
    # get_parent_folder("D:/Users/Wisdom/Allgemein/PJHF/2022_23/Zeltlager/Zeltlagerfilm/Rohmaterial")
    # get_image_date_properties("D:/Users/Wisdom/Allgemein/PJHF/2022_23/Zeltlager/Zeltlagerfilm/Rohmaterial/d-29.07-Samstag/Bilder/07-29-Sa_185.JPG")

    # get_video_date_properties("D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/Basic Tests/tag_pic_vid/Rohmaterial/a Donnerstag 25.07/Videos/sdg (5).MOV")
    # print("".split(", "))
    date = datetime.datetime.now()
    parent = Path(Path.cwd())

    s = Some()
    s.up()