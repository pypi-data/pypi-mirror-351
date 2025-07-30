# Copyright (c) The InverSQL Authors - All Rights Reserved

from pathlib import Path
from typing import Dict, List, Set, Tuple

from data_model import CSVDataManager


class CSVViewerController:
    def __init__(self):
        self.manager = CSVDataManager()
        self.selections: Dict[str, Dict[str, Set]] = {}

    def load_folder(self, folder: Path) -> List[str]:
        return self.manager.load_csv_folder(folder)

    def select_all(self):
        headers, data = self.manager.get_headers_and_data(self.manager.current_csv)
        return set(range(2, len(data) + 2)), set(range(len(headers))), set()

    def get_selection(self, file_path: str) -> Dict[str, Set]:
        return self.selections.get(
            file_path, {"rows": set(), "columns": set(), "cells": set()}
        )

    def save_selection(
        self,
        file_path: str,
        rows: Set[int],
        columns: Set[int],
        cells: Set[Tuple[int, int]],
    ):
        self.selections[file_path] = {
            "rows": rows.copy(),
            "columns": columns.copy(),
            "cells": cells.copy(),
        }

    def toggle_column(
        self,
        col_index: int,
        selected_columns: Set[int],
        selected_cells: Set[Tuple[int, int]],
    ):
        if col_index in selected_columns:
            selected_columns.remove(col_index)
        else:
            selected_columns.add(col_index)
            selected_cells = {c for c in selected_cells if c[1] != col_index}
        return selected_columns, selected_cells

    def toggle_row(
        self,
        row_index: int,
        selected_rows: Set[int],
        selected_cells: Set[Tuple[int, int]],
    ):
        if row_index in selected_rows:
            selected_rows.remove(row_index)
        else:
            selected_rows.add(row_index)
            selected_cells = {c for c in selected_cells if c[0] != row_index}
        return selected_rows, selected_cells

    def toggle_cell(self, row: int, col: int, selected_cells: Set[Tuple[int, int]]):
        key = (row, col)
        if key in selected_cells:
            selected_cells.remove(key)
        else:
            selected_cells.add(key)
        return selected_cells

    def get_headers_and_data(self, file_path: str):
        return self.manager.get_headers_and_data(file_path)
