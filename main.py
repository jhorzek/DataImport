import pandas as pd
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
import DataImport


class DataImportApp:
    def __init__(self, root: ttk.Window):
        self.root = root
        self.root.title("Data Import")
        self.data_frame = None

        # The app has two columns: The left for data import, the right for data preview
        self.left_frame = ttk.Frame(self.root)
        self.right_frame = ttk.Frame(self.root)

        self.right_frame.columnconfigure(0, weight=0)
        self.right_frame.columnconfigure(1, weight=1)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Load Data button
        self.load_data_btn = ttk.Button(
            self.left_frame, text="Load Data", command=self.open_import_window
        )
        self.load_data_btn.grid(row=0, column=0, padx=10, pady=10, sticky="nse")

        # Dataframe to store the imported data
        self.tableview = Tableview(
            self.right_frame,
            paginated=False,
            searchable=True,
            autofit=True,
            coldata=[],
            rowdata=[],
        )
        self.tableview.pack(fill=BOTH, expand=True)

    def open_import_window(self):
        data_frame = DataImport.import_data(self.root)
        if data_frame is not None:
            coldata = list(data_frame.columns)
            rowdata = data_frame.values.tolist()
            self.tableview.build_table_data(
                coldata=coldata,
                rowdata=rowdata,
            )


if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    app = DataImportApp(root)
    root.mainloop()
