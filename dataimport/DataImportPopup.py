import pandas as pd
import re
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, StringVar, IntVar, Toplevel, LabelFrame
from ttkbootstrap.tableview import Tableview


def import_data(root: ttk.Window) -> pd.DataFrame | None:
    """Import data is the main interface for using DataImportPopup. It creates a popup window that allows the user to select a file and import it into a pandas DataFrame.

    Args:
        root (ttk.Window): The root window for the application.

    Returns:
        pd.DataFrame: If the import was successful, a pandas DataFrame is returned. Otherwise, None is returned.
    """
    popup = DataImportPopup(root)
    data_frame = popup.show()
    return data_frame


class CSVOptionsFrame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, *args, **kwargs):
        """Initialize a frame for CSV import options. This will allow the user to specify the separator in the csv files and the missing values encoding.

        Args:
            parent (ttk.Frame): parent frame
        """
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

    def get_separator(self) -> str:
        """Return the user selected separator for the csv file.

        Returns:
            str: separator selected by the user
        """
        return self.separator_options[self.separator_var.get()]

    def get_na_value(self) -> str:
        """Return the user selected NA value (e.g., -999, NaN) for the csv file.

        Returns:
            str: The NA value selected by the user
        """
        if self.missing_values_var.get() == "Default":
            return None
        return self.missing_values_var.get()


class ExcelOptionsFrame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, sheet_names: list[str], *args, **kwargs):
        """Initialize a frame for Excel import options. This will allow the user to specify the sheet name, skip rows, and missing values encoding.

        Args:
            parent (ttk.Frame): parent frame
            sheet_names (list[str]): the names of the sheets in the excel file
        """
        super().__init__(parent, *args, **kwargs)

        # Sheet selector
        self.sheet_var = StringVar(value=sheet_names[0])
        self.sheet_dropdown = ttk.Combobox(
            self,
            textvariable=self.sheet_var,
            values=sheet_names,
        )
        self.sheet_dropdown.pack(pady=5)

        skip_rows_label = ttk.Label(self, text="Skip rows:")
        skip_rows_label.pack(pady=5)
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

    def get_sheet_name(self) -> str:
        """Returns the name of the sheet that the user selected.

        Returns:
            str: sheet name
        """
        return self.sheet_var.get()

    def get_skiprows(self) -> int:
        """Return the number of rows that should be skipped

        Returns:
            int: number of rows to skip
        """
        return self.skiprows_var.get()

    def get_na_value(self) -> str:
        """The missing values encoding that the user selected.

        Returns:
            str: missing values encoding
        """
        if self.missing_values_var.get() == "Default":
            return None
        return self.missing_values_var.get()


class SPSSOptionsFrame(ttk.Frame):
    def __init__(self, parent: ttk.Frame, *args, **kwargs):
        """Initialize a frame for SPSS import options. Currently, no specific settings are supported for SPSS files.

        Args:
            parent (ttk.Frame): parent frame
        """
        super().__init__(parent, *args, **kwargs)


class DataImportPopup(Toplevel):
    def __init__(self, root: ttk.Window):
        """Initialize the DataImportPopup window. This window allows the user to select a file and import it into a pandas DataFrame.

        Args:
            root (ttk.Window): parent window
        """
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
            paginated=True,
            pagesize=25,
            autofit=True,
            coldata=[],
            rowdata=[],
        )
        self.preview_tableview.pack(fill=BOTH, expand=True)

        self.import_btn = None

    def show(self) -> dict[str, pd.DataFrame | str | None]:
        """show the actual window. This function mainly ensures that other windows are waiting for the data import window to close and return the data.

        Returns:
            data_frame (pd.DataFrame): imported data set
            data_name (str): name of the data file
        """
        self.deiconify()
        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)
        # try to get the name of the file
        try:
            # https://stackoverflow.com/questions/9363145/regex-for-extracting-filename-from-path
            filename = re.search("[ \w-]+?(?=\.)", self.filepath).group(0)
        except:
            filename = None
        print(filename)
        return {"data_frame": self.data_frame, "data_name": filename}

    def __select_file(self) -> None:
        """open actual file selector and show the import options for the selected file type."""
        # File selector
        filetypes = (
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx"),
            ("SPSS files", "*.sav"),
            ("All files", "*.*"),
        )
        current_filepath = filedialog.askopenfilename(
            title="Select a file", filetypes=filetypes, parent=self
        )

        # only update the file path if a file was selected
        if current_filepath == "":
            return
        else:
            self.filepath = current_filepath

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
        else:
            ttk.dialogs.dialogs.Messagebox.show_error(
                "Selected file must be one of the following file types: csv, xlsx, .sav.",
                parent=self,
            )
            return

        self.__import_preview_data()

    def __import_preview_data(self) -> None:
        """Imports the data with the selected import options for the specific data file and shows a preview in the tableview."""
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
                try:
                    self.import_options_frame.get_skiprows()
                except Exception as e:
                    ttk.dialogs.dialogs.Messagebox.show_error(
                        "Skip rows must be a number."
                    )
                    return
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

    def __return_data(self, data_frame: pd.DataFrame) -> None:
        """destroy the window and return the data to the main window.

        Args:
            data_frame (pd.DataFrame): imported data set
        """
        # Return the data to the main window
        self.data_frame = data_frame
        self.destroy()
