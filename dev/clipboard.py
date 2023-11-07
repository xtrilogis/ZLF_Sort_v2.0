class ExcelInput(BaseModel):
    excel_folder: Path | None
    excel_file_name: str = f"Zeltlagerfilm {datetime.now().date().year}.xlsx"
    video_columns: List[str] = settings["standard-video-columns"]
    picture_columns: List[str] = settings["standard-picture-columns"]
    override: bool = False


class ExcelConfig(BaseModel):
    excel_folder: Path
    excel_file_name: str = f"Zeltlagerfilm {datetime.now().date().year}.xlsx"
    sheets: List[SheetConfig]


class RawTabInput(BaseModel):
    do_structure: bool
    do_rename: bool
    fill_excel: bool
    create_picture_folder: bool
    raw_material_folder: Path
    first_folder_date: datetime
    excel: Path | ExcelInput | None  # reduzieren auf eines
    picture_folder: Path

# ### old

    # todo
    def get_raw_input(self, excel=None) -> RawTabInput:
        data = {
            "do_structure": self.ui.cb_structure.isChecked(),
            "do_rename": self.ui.cb_rename.isChecked(),
            "fill_excel": self.ui.cb_fill_excel.isChecked(),
            "create_picture_folder": self.ui.cb_diashow.isChecked(),
            "raw_material_folder": Path(self.ui.drop_raw_rawpath.text()),
            "first_folder_date": self.ui.date_correct_fs.date().toPyDate(),
            "excel": excel,
        }
        if self.ui.custom_picture_folder.isChecked():
            if self.ui.drop_picture_folder.text() == "":
                raise ValueError("Bitte gib einen Speicherort für den Bilderordner an.")
            data["picture_folder"] = Path(self.ui.drop_picture_folder.text())
        else:
            data["picture_folder"] = data["raw_material_folder"].parent / "Bilderordner"

        return RawTabInput(**data)

    def get_excel_data(self, override) -> Path | ExcelInput | None:
        if not self.ui.cb_fill_excel:
            return None
        excel_option: ExcelOptions = ExcelOptions(self.ui.excel_option.currentText())
        if excel_option == ExcelOptions.EXISTING:
            return Path(self.ui.drop_raw_excel_file.text())
        else:
            try:
                config = self._get_excel_input(option=excel_option)
                config.override = override
                if (config.excel_folder / config.excel_file_name).exists() and not override:
                    self.open_excel_exists()
                    return
                return config
            except Exception as e:
                traceback.print_exc()
                self.open_problem_input(str(e))

    def _get_excel_input(self, option) -> ExcelInput:
        if option != ExcelOptions.STANDARD and option != ExcelOptions.MANUAL:
            error = "Interner Fehler, der Button 'Excel erstellen'\n" \
                    "sollte nicht klickbar sein mit der Option \n" \
                    "vorhandene Excel nutzen. Neustarten."
            raise ValueError(error)
        elif self.ui.drop_raw_rawpath.text() == "":
            error = "Bitte gib einen Speicherort für die Excel-Datei an.\n" \
                    "Dazu kannst du bei 'Excel-Datei' einen Ordner \n" \
                    "angeben oder für den Standardweg den Rohmaterialorder \nangeben." \
                    "Für Standards schau dir doch gerne die Anleitung an."
            raise ValueError(error)
        else:
            if option == ExcelOptions.MANUAL:
                config = ExcelInput(
                    excel_folder=Path(self.ui.drop_excel_folder.text()),
                    excel_file_name=self.ui.le_excel_file_name.text(),
                    video_columns=self.get_PlainTextEdit_parts(self.ui.vid_columns),
                    picture_columns=self.get_PlainTextEdit_parts(self.ui.pic_columns)
                )
            else:
                config = ExcelInput(
                    excel_folder=Path(self.ui.drop_raw_rawpath.text())
                )
            return config

    # todo
    def run_raw_action(self, function):
        try:
            self.current_function = function
            data: RawTabInput = self.get_raw_input()
        except (ValidationError, ValueError) as e:
            traceback.print_exc()
            self.open_problem_input(error=str(e))
            return
        self.current_function = None
        self.run_action(function=function, slot=self.write_process_raw, input_=data)

    # todo
    def raw_with_excel(self, function, override=False):
        try:
            self.current_function = function
            data: RawTabInput = self.get_raw_input(self.get_excel_data(override=override))
        except (ValidationError, ValueError) as e:
            traceback.print_exc()
            self.open_problem_input(error=str(e))
            return
        self.current_function = None
        self.run_action(function=function, slot=self.write_process_raw, input_=data)