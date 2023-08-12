"""Calculate some basic statistics"""
from pathlib import Path
from typing import List, Any

from moviepy.editor import VideoFileClip
import os
import time
from assets.constants import video_extensions


def get_raw_material_duration(path: Path):
    total_duration = 0.0
    problems: List[str] = []
    duration_per_day: List[List[Any]] = []
    try:
        folders = os.listdir(path)
        for folder in folders:
            if os.path.isdir(folder):
                current_day_duration = 0
                for root, _, files in os.walk(os.path.join(path, folder)):
                    for file in files:
                        _, ext = os.path.splitext(file)
                        if ext in video_extensions:
                            duration = get_duration(root, file)
                            total_duration += duration
                            current_day_duration += duration
                duration_per_day.append(
                    [
                        folder,
                        time.strftime("%H:%M:%S", time.gmtime(current_day_duration)),
                    ]
                )
        return total_duration, problems, duration_per_day
    except Exception as e:
        return -1.0, [], []


def get_duration(root, file):
    file_fullpath = os.path.join(root, file)
    try:
        duration = VideoFileClip(file_fullpath).duration
        print(f"File: {file}, Dauer: {duration}s")
        return duration
    except Exception as e:
        problems.append(file_fullpath)
        return 0


def count_all(path: Path) -> int:
    """Count all files in the given directory"""
    total = 0
    for root, _, files in os.walk(path):
        for file in files:
            total += 1
    return total


def percent_selected(raw: Path, selected: Path) -> str:
    raw_num = count_all(raw)
    sel_num = count_all(selected)
    return f"{sel_num} von {raw_num} benutzt. ({sel_num/raw_num*100}%)"


if __name__ == "__main__":
    roots = "D:\\Users\\Wisdom\\Lernen\\Coding_Python\\Zlf_sort\\Dateien\\Test dateien\\2022\\Zeltlager 2022\\Zeltlagerfilm 2022\\Rohmaterial\\"
    total_duration, problems, duration_per_day = get_raw_material_duration(Path(roots))
    print(
        f'Summe: {total_duration}s | {time.strftime("%H:%M:%S", time.gmtime(total_duration))}\n'
        f"Probleme: {problems}\n"
        f"Tage: {duration_per_day}"
    )
