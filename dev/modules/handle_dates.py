import os
import struct
import time
from datetime import datetime as dt
pfad = "D:/Users/Wisdom/Lernen/Coding_Python/Zlf_sort/Dateien/level9000/Rohmaterial always copy/b Donnerstag 25.07/"

# INTEGRIEREN und umbenennen probieren einfach hier mit raname 1 2 3 ...
# ############ Test mit Bildern -> sollten nicht verändert werden
# ############ Test mit 2 Ordnern
#
# ohne Excel
# dann mit x markierte 2Std. implementieren
# 2 " std. Code verbesseren alle path + file in join,
# pylint, sprechende Variablen -> name nur gleich, wenn auch gleicher Inhalt nicht
# 3 versch path, path_data
def problem_with_Media_created(path_data):
    for root, _, files in os.walk(path_data):
        for file in files:
            print(file)
            filename, file_ext = os.path.splitext(file)
            if file_ext != ".MOV":
                print("not mov")
                pass
            else:
                new_date = get_Media_created(os.path.join(root, file))
                print(type(new_date))
                if type(new_date) == bool:
                    pass
                else:
                    new_mtime = time.mktime(new_date.timetuple())
                    os.utime(root+file, (new_mtime, new_mtime))  # os.path.getatime(root+file)
                    print("Modification Date changed")
        files.sort(key=lambda x: os.path.getmtime(os.path.join(root, x)), reverse=False)
        print(files)
    return True


def get_Media_created(file_path):
    ATOM_HEADER_SIZE = 8
    EPOCH_ADJUSTER = 2082844800
    creation_time = None
    with open(file_path, "rb") as f:
        while True:
            atom_header = f.read(ATOM_HEADER_SIZE)
            if atom_header[4:8] == b'moov':
                break  # found
            else:
                atom_size = struct.unpack('>I', atom_header[0:4])[0]
                f.seek(atom_size - 8, 1)

        # found 'moov', look for 'mvhd' and timestamps
        atom_header = f.read(ATOM_HEADER_SIZE)
        if atom_header[4:8] == b'cmov':
            return False
        elif atom_header[4:8] != b'mvhd':
            print(file_path)
            print("No access to 'Media created'. Please input Date manually:")  # 'expected to find "mvhd" header.')

            creation_time = input_date()
            return creation_time
        else:
            f.seek(4, 1)
            creation_time = struct.unpack('>I', f.read(4))[0] - EPOCH_ADJUSTER
            creation_time = dt.fromtimestamp(creation_time)
            if creation_time.year < 1990:  # invalid or censored data
                print("Something is wrong with the timestamp")
                return False
        modTime = time.mktime(creation_time.timetuple())
        os.utime(file_path, (modTime, modTime))
    return creation_time


def input_date():
    # text = input("03.07.2019 19:44:00: ")
    text = "25.07.2019 14:33:20"
    date_time = text.split(" ")
    date = date_time[0].split(".")
    time = date_time[1].split(":")
    year, month, day = int(date[2]), int(date[1]), int(date[0])
    hour, minute, second = int(time[0]), int(time[1]), int(time[2])
    date = dt(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
    return date

if __name__ == "__main__":
    print(problem_with_Media_created(pfad))
    # print(input_date())

