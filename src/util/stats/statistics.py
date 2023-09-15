"""Calculate some basic statistics"""
from pathlib import Path
from typing import List, Any, Tuple
from moviepy.editor import VideoFileClip
import os
import time

from assets.constants import video_extensions


def get_raw_material_duration(path: Path) -> Tuple[str, List[str], List[List[Any]]]:
    total_duration = 0.0
    problems: List[str] = []
    duration_per_day: List[List[Any]] = []

    for folder in path.iterdir():
        if folder.is_dir():
            current_day_duration = 0
            for element in folder.glob('**/*'):
                if element.suffix in video_extensions:
                    try:
                        duration = _get_duration(element)
                        total_duration += duration
                        current_day_duration += duration
                    except AttributeError:
                        problems.append(element.name)
            duration_per_day.append(
                    [
                        folder.name,
                        time.strftime("%H:%M:%S", time.gmtime(current_day_duration)),
                    ]
                )
    return time.strftime("%H:%M:%S", time.gmtime(total_duration)), problems, duration_per_day


def _get_duration(file_fullpath: Path):
    duration = VideoFileClip(str(file_fullpath)).duration
    print(f"File: {file_fullpath.name}, Dauer: {duration}s")
    return duration


def percent_selected(raw: Path, selected: Path) -> str:
    raw_num = _count_all(raw)
    sel_num = _count_all(selected)
    return f"{sel_num} von {raw_num} benutzt. ({sel_num/raw_num*100}%)"


def _count_all(path: Path) -> int:
    """Count all files in the given directory"""
    total = 0
    for root, _, files in os.walk(path):
        total += len(files)
    return total
