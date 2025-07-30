# SPDX-FileCopyrightText: 2025 Dimitris Kardarakos
# SPDX-License-Identifier: AGPL-3.0-only

from textual.widget import Widget
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static, Label
from textual.containers import HorizontalGroup
from textual.message import Message


class FretboardUiCell(Widget):
    """Controls the display and behavior of a fretboard cell"""

    DEFAULT_CSS = """
    FretboardUiCell {
        width: 7;
        height: 1;
        background: $surface;
        border-right: vkey $background;
        border-left: vkey $background;
        align: center middle;
        text-wrap: nowrap;
        layers: below above;
     }
    """

    CELL_TEXT = "---"
    STRING_TEXT = "-------------"  # DEFAULT_CELL_TEXT = "           "

    cell_text: reactive[str] = reactive(CELL_TEXT, recompose=True)

    def __init__(self, *args, string: int, fret: int, **kwargs):
        self.string = string
        self.fret = fret

        super().__init__(*args, **kwargs)

    class Pluck(Message):
        """Message for mouse click on a fretboard cell"""

        def __init__(self, string: int, fret: int) -> None:
            self.string = string
            self.fret = fret
            super().__init__()

    class Enter(Message):
        """Message for mouse enter on a fretboard cell"""

        def __init__(self, string: int, fret: int) -> None:
            self.string = string
            self.fret = fret
            super().__init__()

    class Leave(Message):
        """Message for mouse leave from a fretboard cell"""

        def __init__(self, string: int, fret: int) -> None:
            self.string = string
            self.fret = fret
            super().__init__()

    class FretboardUiCellString(Static):
        """Controls display a string on the fretboard cell"""

        DEFAULT_CSS = """
        FretboardUiCellString{
            layer: below;
            width: 1fr;
            height: 1fr;
            text-align: center;
            # align: center middle;
       }
        """

    class FretboardUiCellContent(Label):
        """Text content displayed in a cell"""

        DEFAULT_CSS = """
        FretboardUiCellContent{
            layer: above;
            # width: 3;
            height: 1fr;
            text-align: center;
            # align: center middle;
       }
        """

    @staticmethod
    def at(string: int, fret: int) -> str:
        """Get the ID of the fretboard cell at the given location."""
        return f"cell-{string}-{fret}"

    def default_cell_text(self):
        """The default text that should be displayed in a cell"""
        return self.CELL_TEXT if self.fret != 0 else "o"

    def compose(self) -> ComposeResult:
        yield self.FretboardUiCellString(self.STRING_TEXT if self.fret != 0 else "o")
        yield self.FretboardUiCellContent(
            self.cell_text, id=f"cell-content-{self.string}-{self.fret}"
        )

    # pylint: disable=C0116
    def on_click(self) -> None:
        self.post_message(self.Pluck(self.string, self.fret))

    def on_enter(self) -> None:
        self.post_message(self.Enter(self.string, self.fret))

    def on_leave(self) -> None:
        self.post_message(self.Leave(self.string, self.fret))


class FretboardUiRow(HorizontalGroup):
    """Contains a row of cells"""

    DEFAULT_CSS = """
    FretboardUiRow{
        width: 1fr;
        height: 1;
        content-align: center middle;
    }
    """


class FretboardUiSign(Static):
    """Signs displayed below the fretboard"""

    DEFAULT_CSS = """
    FretboardUiSign{
        width: 7;
        height: 1;
        text-align: center;
   }
    """


class FretboardUi(Widget):
    """Controls the display of the fretboard"""

    NUM_OF_STRINGS = 6
    NUM_OF_FRETS = 16

    num_of_frets: reactive[int] = reactive(NUM_OF_FRETS)

    def compose(self) -> ComposeResult:
        """Compose the fretboard grid"""

        for string in range(1, self.NUM_OF_STRINGS + 1):
            yield FretboardUiRow(
                *[
                    FretboardUiCell(
                        id=FretboardUiCell.at(string, fret_num),
                        string=string,
                        fret=fret_num,
                    )
                    for fret_num in range(self.num_of_frets)
                ],
            )

        yield HorizontalGroup(
            *[
                FretboardUiSign(sign_text, id=f"sign-{sign_col}")
                for sign_col, sign_text in enumerate(self._signs())
            ]
        )

    def fretboard_ui_cell(self, string: int, fret: int) -> FretboardUiCell:
        """Get the cell at a given location."""
        return self.query_one(f"#{FretboardUiCell.at(string,fret)}", FretboardUiCell)

    def _signs(self) -> list:
        signs_list = []
        for f in range(0, self.num_of_frets):
            if f in (3, 5, 7, 9, 15, 17, 19, 21):
                sign_text = "."
            elif f in (12, 24):
                sign_text = ". ."
            else:
                sign_text = ""
            signs_list.append(sign_text)

        return signs_list

    # pylint: disable=C0116,W0201
    def on_mount(self) -> None:
        self.theme = "textual-light"

        for string in range(1, self.NUM_OF_STRINGS + 1):
            for col in range(self.NUM_OF_FRETS):
                c = self.fretboard_ui_cell(string, col)
                c.styles.width = 5 if col == 0 else f"{self.num_of_frets * 3 - col}fr"

        for sign_col in range(self.NUM_OF_FRETS):
            sign = self.query_one(f"#sign-{sign_col}")
            sign.styles.width = (
                3 if sign_col == 0 else f"{self.num_of_frets * 3 - sign_col}fr"
            )
