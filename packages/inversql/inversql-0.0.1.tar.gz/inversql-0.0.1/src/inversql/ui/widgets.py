# Copyright (c) The InverSQL Authors - All Rights Reserved

from pathlib import Path

from textual.app import ComposeResult
from textual.widgets import Label, ListItem


class CSVListItem(ListItem):
    def __init__(self, path: str) -> None:
        super().__init__()
        self.path = path
        self.label = Label(Path(path).name)

    def compose(self) -> ComposeResult:
        yield self.label
