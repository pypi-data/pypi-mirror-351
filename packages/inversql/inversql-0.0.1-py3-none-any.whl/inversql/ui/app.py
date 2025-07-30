# Copyright (c) The InverSQL Authors - All Rights Reserved

from pathlib import Path
from typing import List

from controller import CSVViewerController
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, DataTable, Input, ListView, Static
from widgets import CSVListItem


class MultiCSVViewerApp(App):
    CSS_PATH = "multi_csv_viewer.tcss"
    selected_rows = reactive(set)
    selected_columns = reactive(set)
    selected_cells = reactive(set)

    def __init__(self):
        super().__init__()
        self.controller = CSVViewerController()
        self.table = DataTable()

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("CSV Files", classes="title")
                yield ListView(id="csv-list")
            with Container(id="main"):
                yield self.table
            with Vertical(id="right-panel"):
                yield Static("Folder Selector", classes="title")
                yield Input(placeholder="Path to folder with CSVs", id="folder-path")
                yield Button("Reload Folder", id="reload-folder")

    def on_mount(self) -> None:
        base_dir = Path(__file__).parent.parent.resolve()  # inversql/inversql/
        default_folder = (
            base_dir.parent.parent / "data"
        )  # goes up two levels to inversql/, then scripts/data
        self.query_one("#folder-path", Input).value = str(default_folder)
        self.load_csv_folder(default_folder)

    def load_csv_folder(self, folder: Path) -> None:
        try:
            files = self.controller.load_folder(folder)
            list_view = self.query_one("#csv-list", ListView)
            list_view.clear()
            for path in files:
                list_view.append(CSVListItem(path))
            if files:
                self.controller.current_csv = files[0]
                self.restore_selection()
                self._render_table()
        except ValueError as e:
            self.notify(str(e), severity="error")

    def restore_selection(self) -> None:
        sel = self.controller.get_selection(self.controller.current_csv)
        self.selected_rows = sel["rows"].copy()
        self.selected_columns = sel["columns"].copy()
        self.selected_cells = sel["cells"].copy()

    def save_selection(self) -> None:
        self.controller.save_selection(
            self.controller.current_csv,
            self.selected_rows,
            self.selected_columns,
            self.selected_cells,
        )

    def _column_label(self, index: int) -> str:
        label = ""
        while True:
            index, rem = divmod(index, 26)
            label = chr(65 + rem) + label
            if index == 0:
                break
            index -= 1
        return label

    def _calculate_column_widths(
        self, headers: List[str], data: List[List[str]]
    ) -> List[int]:
        return [
            max(len(headers[i]), *(len(str(row[i])) for row in data)) + 2
            for i in range(len(headers))
        ]

    def _render_table(self) -> None:
        file_path = self.controller.current_csv
        headers, data = self.controller.get_headers_and_data(file_path)
        self.table.clear(columns=True)
        if not headers:
            return

        col_widths = self._calculate_column_widths(headers, data)
        self.table.add_column("", width=5)
        for w in col_widths:
            self.table.add_column("", width=w)

        # Column labels (A, B, ...)
        label_row = [Text("     ")]
        for i in range(len(headers)):
            label = self._column_label(i)
            text = Text(
                ("✅ " if i in self.selected_columns else "  ") + label, style="bold"
            )
            if i in self.selected_columns:
                text.stylize("on rgb(70,70,120)")
            label_row.append(text)
        self.table.add_row(*label_row)

        # Headers
        header_row = [Text("     ")]
        for i, header in enumerate(headers):
            text = Text(header, style="bold white on black")
            if i in self.selected_columns:
                text.stylize("on rgb(70,70,120)")
            header_row.append(text)
        self.table.add_row(*header_row)

        # Data
        for row_idx, row in enumerate(data):
            vis_row = row_idx + 2
            row_selected = vis_row in self.selected_rows
            row_label = Text(
                f"{'✅' if row_selected else ' '} {vis_row - 1}", style="bold"
            )
            if row_selected:
                row_label.stylize("on rgb(70,70,120)")
            row_cells = [row_label]
            for col_idx, cell in enumerate(row):
                selected = (
                    (vis_row, col_idx) in self.selected_cells
                    or row_selected
                    or col_idx in self.selected_columns
                )
                text = Text(f" {cell} ")
                if selected:
                    text.stylize("on rgb(70,70,120)")
                row_cells.append(text)
            self.table.add_row(*row_cells)

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        row, col = event.coordinate.row, event.coordinate.column
        headers, data = self.controller.get_headers_and_data(
            self.controller.current_csv
        )

        if row == 0 and col == 0:
            if len(self.selected_rows) == len(data) and len(
                self.selected_columns
            ) == len(headers):
                self.selected_rows.clear()
                self.selected_columns.clear()
            else:
                self.selected_rows = set(range(2, len(data) + 2))
                self.selected_columns = set(range(len(headers)))
            self.selected_cells.clear()
        elif row == 0:
            col_index = col - 1
            if col_index in self.selected_columns:
                self.selected_columns.remove(col_index)
            else:
                self.selected_columns.add(col_index)
                self.selected_cells = {
                    cell for cell in self.selected_cells if cell[1] != col_index
                }
            self.selected_rows.clear()
        elif col == 0:
            if row in self.selected_rows:
                self.selected_rows.remove(row)
            else:
                self.selected_rows.add(row)
                self.selected_cells = {
                    cell for cell in self.selected_cells if cell[0] != row
                }
            self.selected_columns.clear()
        else:
            cell_key = (row, col - 1)
            if cell_key in self.selected_cells:
                self.selected_cells.remove(cell_key)
            else:
                self.selected_cells.add(cell_key)
            self.selected_rows.clear()
            self.selected_columns.clear()

        self.save_selection()
        self._render_table()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if isinstance(event.item, CSVListItem):
            self.save_selection()
            self.controller.current_csv = event.item.path
            self.restore_selection()
            self._render_table()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "reload-folder":
            folder_path = self.query_one("#folder-path", Input).value
            self.load_csv_folder(Path(folder_path))
