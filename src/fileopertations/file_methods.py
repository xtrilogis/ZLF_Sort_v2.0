import shutil
from pathlib import Path


def copy_file(src_file: Path, dst_folder: Path):
    if not dst_folder.exists():
        dst_folder.mkdir(parents=True)
    file_dst = dst_folder / src_file.name
    counter = 1
    while file_dst.exists():
        file_dst = dst_folder / f'{src_file.stem}({counter}){src_file.suffix}'
        counter += 1
    shutil.copy(src=src_file, dst=file_dst)
