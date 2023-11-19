from src.main.runner.runners import run_raw_processes

from assethandling.basemodels import RawTabInput
from src.main.connectors import raw_connector


def decor(func):
    def wrap(*args, **kwargs):
        print("==========")
        func(*args, **kwargs)
        print("==========")

    return wrap


@decor
def print_text2(name):
    print(name)
    function()


def function():
    print("bla")


def run_create_picture_folder(inputs: RawTabInput, progress_callback, get_data) -> str:
    result = run_raw_processes(function=raw_connector.handle_create_picture_folder,
                      titel="Bilderordner erstellen.",
                      progress_callback=progress_callback,
                      folder=inputs.picture_folder,
                      raw_material_folder=inputs.raw_material_folder)
    # result.append("Bilderordner erstellen abgeschlossen.")
    # return result
    return "Bilderordner erstellen abgeschlossen."
def raw_process2(titel):
    def decor(func):
        def wrap(*args, **kwargs):
            progress_callback = kwargs["progress_callback"]

            if not is_valid_folder(kwargs["inputs"].raw_material_folder):
                raise ValueError("Bitte gib einen gültigen Rohmaterial ordner an.")
            progress_callback.emit("Inputs validiert")

            result = func(*args, **kwargs)
            pretty_send_problems(titel=titel, list_=result, progress_callback=progress_callback)
            return f"{titel} abgeschlossen."

        return wrap

    return decor
print_text2("assd")
