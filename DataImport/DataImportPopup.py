import pandas as pd
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, StringVar, IntVar, Toplevel, LabelFrame
from ttkbootstrap.tableview import Tableview


def import_data(root) -> pd.DataFrame:
    popup = DataImportPopup(root)
    data_frame = popup.show()
    return data_frame


class CSVOptionsFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Separator options for CSV
        separator_label = ttk.Label(self, text="Separator (CSV only):")
        separator_label.pack(pady=5)

        self.separator_options = {",": ",", ";": ";", "Space": " ", "Tab": "\t"}
        self.separator_var = StringVar(value=",")
        self.separator_dropdown = ttk.Combobox(
            self,
            textvariable=self.separator_var,
            values=list(self.separator_options.keys()),
        )
        self.separator_dropdown.pack(pady=5)

        # Missing values encoding
        missing_values_label = ttk.Label(self, text="Missing values encoding:")
        missing_values_label.pack(pady=5)

        self.missing_values_var = StringVar(value="Default")
        self.missing_values_entry = ttk.Entry(
            self, textvariable=self.missing_values_var
        )
        self.missing_values_entry.pack(pady=5)

    def get_separator(self):
        return self.separator_options[self.separator_var.get()]

    def get_na_value(self):
        if self.missing_values_var.get() == "Default":
            return None
        return self.missing_values_var.get()


class ExcelOptionsFrame(ttk.Frame):
    def __init__(self, parent, sheet_names: list[str], *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Sheet selector
        self.sheet_var = StringVar(value=sheet_names[0])
        self.sheet_dropdown = ttk.Combobox(
            self,
            textvariable=self.sheet_var,
            values=sheet_names,
        )
        self.sheet_dropdown.pack(pady=5)

        self.skiprows_var = IntVar(value=0)
        self.skiprows_selector = ttk.Entry(self, textvariable=self.skiprows_var)
        self.skiprows_selector.pack(pady=5)

        # Missing values encoding
        missing_values_label = ttk.Label(self, text="Missing values encoding:")
        missing_values_label.pack(pady=5)

        self.missing_values_var = StringVar(value="Default")
        self.missing_values_entry = ttk.Entry(
            self, textvariable=self.missing_values_var
        )
        self.missing_values_entry.pack(pady=5)

    def get_sheet_name(self):
        return self.sheet_var.get()

    def get_skiprows(self):
        return self.skiprows_var.get()

    def get_na_value(self):
        if self.missing_values_var.get() == "Default":
            return None
        return self.missing_values_var.get()


class SPSSOptionsFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


class DataImportPopup(Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.title("Select Dataset")

        self.data_frame = None

        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=LEFT, padx=10, pady=10, fill=Y)

        # Select File button
        self.select_file_btn = ttk.Button(
            self.left_frame, text="Select File", command=self.__select_file
        )
        self.select_file_btn.pack(pady=5)
        self.show_preview = ttk.IntVar(value=1)
        self.show_preview_selection = ttk.Checkbutton(
            self.left_frame,
            text="Show data preview",
            variable=self.show_preview,
            onvalue=1,
            offvalue=0,
        )
        self.show_preview_selection.pack(pady=5)

        # Placeholder for specifications of how to import the file
        self.import_options_frame = None

        # Frame for the right side (Table preview)
        self.right_frame = LabelFrame(self, text="Data Preview")
        self.right_frame.pack(side=RIGHT, padx=10, pady=10, fill=BOTH, expand=True)

        # Tableview for data preview
        self.preview_tableview = Tableview(
            self.right_frame,
            paginated=False,
            searchable=True,
            autofit=True,
            coldata=[],
            rowdata=[],
        )
        self.preview_tableview.pack(fill=BOTH, expand=True)

        self.import_btn = None

    def show(self):
        self.deiconify()
        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)
        return self.data_frame

    def __select_file(self):
        # File selector
        filetypes = (
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx"),
            ("SPSS files", "*.sav"),
            ("All files", "*.*"),
        )
        self.filepath = filedialog.askopenfilename(
            title="Select a file", filetypes=filetypes
        )

        # show the options for this file type
        if self.import_options_frame is not None:
            self.import_options_frame.forget()
        if self.filepath.endswith(".csv"):
            self.import_options_frame = CSVOptionsFrame(self.left_frame)
            self.import_options_frame.pack(pady=5)
            # Refresh button with a refresh symbol
            refresh_btn = ttk.Button(
                self.import_options_frame,
                text="Refresh Preview ⟳",
                command=self.__import_preview_data,
            )
            refresh_btn.pack(pady=5)
        elif self.filepath.endswith(".xlsx"):
            self.import_options_frame = ExcelOptionsFrame(
                self.left_frame, sheet_names=pd.ExcelFile(self.filepath).sheet_names
            )
            self.import_options_frame.pack(pady=5)
            # Refresh button with a refresh symbol
            refresh_btn = ttk.Button(
                self.import_options_frame,
                text="Refresh Preview ⟳",
                command=self.__import_preview_data,
            )
            refresh_btn.pack(pady=5)
        elif self.filepath.endswith(".sav"):
            self.import_options_frame = SPSSOptionsFrame(self.left_frame)
            self.import_options_frame.pack(pady=5)

        self.__import_preview_data()

    def __import_preview_data(self):
        # Load the selected file based on type and separator
        if self.filepath.endswith(".csv"):
            try:
                df = pd.read_csv(
                    self.filepath,
                    sep=self.import_options_frame.get_separator(),
                    na_values=self.import_options_frame.get_na_value(),
                )
            except Exception as e:
                return
        elif self.filepath.endswith(".xlsx"):
            try:
                df = pd.read_excel(
                    self.filepath,
                    sheet_name=self.import_options_frame.get_sheet_name(),
                    skiprows=self.import_options_frame.get_skiprows(),
                    na_values=self.import_options_frame.get_na_value(),
                )
            except Exception as e:
                return
        elif self.filepath.endswith(".sav"):
            try:
                df = pd.read_spss(self.filepath)
            except Exception as e:
                return
        else:
            return

        # Update Tableview with the imported data
        if self.show_preview.get() == 1:
            coldata = list(df.columns)
            rowdata = df.values.tolist()
            self.preview_tableview.build_table_data(
                coldata=coldata,
                rowdata=rowdata,
            )
        else:
            self.preview_tableview.build_table_data(
                coldata=[],
                rowdata=[],
            )

        # add import button
        if self.import_btn is not None:
            self.import_btn.forget()

        self.import_btn = ttk.Button(
            self.import_options_frame,
            text="Import",
            command=lambda data=df: self.__return_data(data_frame=data),
        )
        self.import_btn.pack(pady=20)

    def __return_data(self, data_frame):
        # Return the data to the main window
        self.data_frame = data_frame
        self.destroy()
