# Copyright (c) The InverSQL Authors - All Rights Reserved

import csv
from pathlib import Path
from typing import Dict, List, Tuple


class CSVDataManager:
    def __init__(self):
        self.csv_data: Dict[str, Tuple[List[str], List[List[str]]]] = {}
        self.selections: Dict[str, Dict[str, set]] = {}
        self.current_csv: str = ""
        self.files = []

    def load_csv_folder(self, folder: Path) -> List[str]:
        self.csv_data.clear()
        self.selections.clear()
        self.current_csv = ""

        if not folder.exists() or not folder.is_dir():
            raise ValueError("Invalid folder path")

        loaded_files = []
        for csv_path in folder.glob("*.csv"):
            if self.load_csv(str(csv_path)):
                loaded_files.append(str(csv_path))

        return loaded_files

    def load_csv(self, file_path: str) -> bool:
        try:
            with open(file_path, newline="") as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)
                data = [row for row in reader]

            self.csv_data[file_path] = (headers, data)
            self.selections.setdefault(
                file_path, {"rows": set(), "columns": set(), "cells": set()}
            )

            if not self.current_csv:
                self.current_csv = file_path

            return True
        except Exception:
            return False

    def get_headers_and_data(self, file_path: str) -> Tuple[List[str], List[List[str]]]:
        return self.csv_data.get(file_path, ([], []))

    def get_selection(self, file_path: str) -> Dict[str, set]:
        return self.selections.get(
            file_path, {"rows": set(), "columns": set(), "cells": set()}
        )

    def save_selection(
        self, file_path: str, rows: set, columns: set, cells: set
    ) -> None:
        self.selections[file_path] = {
            "rows": rows.copy(),
            "columns": columns.copy(),
            "cells": cells.copy(),
        }
