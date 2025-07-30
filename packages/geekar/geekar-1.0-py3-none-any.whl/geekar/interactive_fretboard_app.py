# SPDX-FileCopyrightText: 2025 Dimitris Kardarakos
# SPDX-License-Identifier: AGPL-3.0-only

from time import sleep
from textual import on
from textual import events
from textual.app import App, ComposeResult
from textual.containers import (
    VerticalGroup,
    HorizontalGroup,
    Grid,
    VerticalScroll,
    Container,
)
from textual.widgets import (
    Footer,
    Header,
    Label,
    Static,
    Select,
    Switch,
    Rule,
    Collapsible,
    Digits,
    Input,
    Button,
)
from textual.validation import Number
from textual.widget import Widget
from textual.reactive import reactive
from music21.pitch import Pitch
from music21.key import Key
import fluidsynth
from geekar.geekar_logger import logger
from geekar.caged_system import CagedSystem
from geekar.fretboard_ui import FretboardUi, FretboardUiCell
from geekar.midi import MidiSynth, note_to_midi, GUITAR_MIDI_INSTRUMENTS
from geekar import geekar_types

DEFAULT_KEY_NAME = ""
DEFAULT_KEY_TYPE = "M"
MAJOR_KEY_NAMES = [
    "C",
    "Db",
    "D",
    "Eb",
    "E",
    "F",
    "F#",
    "Gb",
    "G",
    "Ab",
    "A",
    "Bb",
    "B",
]
MINOR_KEY_NAMES = [
    "C",
    "C#",
    "D",
    "D#",
    "Eb",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "Bb",
    "B",
]
KEY_TYPES = [
    ("major", "M"),
    ("natural minor", "nm"),
    ("major pentatonic", "MP"),
    ("minor pentatonic", "mp"),
]
CAGED_BACKGROUND_LEGEND = {
    "C": "c-background-pattern",
    "A": "a-background-pattern",
    "G": "g-background-pattern",
    "E": "e-background-pattern",
    "D": "d-background-pattern",
}
CAGED_TEXT_COLOR_LEGEND = {
    "C": "c-text-color-pattern",
    "A": "a-text-color-pattern",
    "G": "g-text-color-pattern",
    "E": "e-text-color-pattern",
    "D": "d-text-color-pattern",
}
DIATONIC_FRET_CONTENT_OPTIONS = [
    ("Scale notes", "sn"),
    ("Degrees", "dg"),
    ("Degree Triads", "dt"),
]
PENTATONIC_FRET_CONTENT_OPTIONS = [
    ("Scale notes", "sn"),
    ("Degrees", "dg"),
]
MINOR_KEY_FLAT_DEGREES = {3, 6, 7}


class InstrumentSelectorWidget(Static):
    # pylint: disable=C0115, C0116
    def compose(self) -> ComposeResult:
        yield Select(
            GUITAR_MIDI_INSTRUMENTS.items(),
            # [(instrument, i) for i, instrument in enumerate(GENERAL_MIDI_INSTRUMENTS)],
            id="instrument-selector",
            allow_blank=False,
            prompt="Select instrument:",
            value=app.instrument,
        )

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        if event.value is not None:

            app.instrument = int(str(event.value))
            app.midi_synth.select_midi_program(event.value)


class KeyTypeSelectorWidget(Static):
    # pylint: disable=C0115, C0116
    def compose(self) -> ComposeResult:
        yield Select(
            KEY_TYPES,
            id="key-type-selector",
            value=app.key_type,
            allow_blank=False,
            prompt="Key type:",
        )

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        app.key_type = str(event.value)
        key_name_selector = app.query_one("#key-name-selector", Select)
        key_name_selector.value = Select.BLANK
        app.key_name = ""
        key_name_selector_widget = app.query_one(
            "#key-name-selector-widget", KeyNameSelectorWidget
        )
        key_name_selector_widget.key_names = (
            MAJOR_KEY_NAMES if str(event.value) in ["M", "MP"] else MINOR_KEY_NAMES
        )
        fret_content_selector = app.query_one(
            "#fret-content-selector-widget", FretContentSelectorWidget
        )
        fret_content_selector.options = (
            DIATONIC_FRET_CONTENT_OPTIONS
            if str(event.value) in ("M", "m")
            else PENTATONIC_FRET_CONTENT_OPTIONS
        )
        app.decorate_fretboard()


class KeyNameSelectorWidget(Static):
    # pylint: disable=C0115, C0116
    key_names: reactive[list] = reactive(
        (MAJOR_KEY_NAMES if DEFAULT_KEY_TYPE in ["M", "MP"] else MINOR_KEY_NAMES),
        recompose=True,
    )

    def compose(self) -> ComposeResult:
        yield Select(
            [(key_name, key_name) for key_name in self.key_names],
            id="key-name-selector",
            value=app.key_name if app.key_name else Select.BLANK,
            allow_blank=True,
            prompt="Key name:",
        )

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        app.key_name = str(event.value) if event.value != Select.BLANK else ""
        app.set_widget_availability()
        app.decorate_fretboard()


class FretContentSelectorWidget(Static):
    # pylint: disable=C0115, C0116
    options: reactive[list] = reactive(
        list(DIATONIC_FRET_CONTENT_OPTIONS), recompose=True
    )

    def compose(self) -> ComposeResult:
        yield Select(
            self.options,
            id="fret-content-selector",
            prompt="Fret content:",
            allow_blank=True,
        )

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        app.fret_content = str(event.value)
        app.set_widget_availability()
        app.decorate_fretboard()


class DegreeSelectorWidget(Static):
    # pylint: disable=C0115, C0116
    def compose(self) -> ComposeResult:
        yield Select(
            [(str(degree), degree) for degree in range(1, 8)],
            id="degree-selector",
            value=app.degree,
            allow_blank=False,
            prompt="Degree:",
        )

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        app.degree = int(str(event.value))
        app.decorate_fretboard()


class TuningSelectorWidget(Static):
    # pylint: disable=C0115, C0116
    def compose(self) -> ComposeResult:
        yield Select(
            [(tuning, tuning) for tuning, _ in geekar_types.TUNING.items()],
            id="tuning-selector",
            value=app.tuning,
            allow_blank=False,
            prompt="Tuning:",
        )

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        app.tuning = str(event.value)
        app.decorate_fretboard()
        # app.clear_widget_state()
        app.set_widget_availability()


class PatternSetWidget(Widget):
    # pylint: disable=C0115, C0116
    def compose(self) -> ComposeResult:
        with HorizontalGroup():
            for pattern_name in "CAGED":
                with VerticalGroup():
                    yield Label(
                        pattern_name,
                        name=pattern_name,
                        id=f"{str.lower(pattern_name)}-pattern-switch-label",
                        classes="pattern-switch-label",
                    )
                    yield Rule(
                        id=f"{str.lower(pattern_name)}-pattern-switch-rule",
                        name=pattern_name,
                        line_style="thick",
                        classes=str(CAGED_BACKGROUND_LEGEND.get(pattern_name)),
                    )
                    yield Container(
                        Switch(
                            id=f"{str.lower(pattern_name)}-pattern-switch",
                            name=pattern_name,
                            classes="pattern-switch",
                        ),
                        classes="pattern-switch-container",
                    )
            yield Label("   ")
            with VerticalGroup():
                yield Label(
                    "All",
                    name="all",
                    id="all-pattern-switch-label",
                    classes="pattern-switch-label",
                )
                yield Rule(
                    id="all-pattern-switch-rule",
                    name="all",
                    line_style="thick",
                    classes="all-background-pattern",
                )
                yield Container(
                    Switch(
                        id="all-pattern-switch",
                        name="all-patterns",
                        classes="pattern-switch",
                    ),
                    classes="pattern-switch-container",
                )

    @on(events.Click, "Label")
    @on(events.Click, "Rule")
    def on_click(self, event: events.Click) -> None:
        """Make the label toggle the switch."""
        event.stop()
        if event.widget is not None:
            self.query_one(
                f"#{str.lower(str(event.widget.name))}-pattern-switch", Switch
            ).toggle()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.name == "all-patterns":
            for pattern_name in "caged":
                caged_switch = self.query_one(f"#{pattern_name}-pattern-switch", Switch)
                caged_switch.value = event.value
                caged_switch.disabled = event.value

        else:
            if event.value:
                app.active_patterns.append(event.switch.name)
            else:
                app.active_patterns.remove(event.switch.name)

        app.decorate_fretboard()


class PlayTypeSelectorWidget(Widget):
    # pylint: disable=C0115, C0116, W0613
    def compose(self) -> ComposeResult:
        yield Select(
            [("Scale", "s"), ("Metronome", "m")],
            id="play-type-selector",
            value="m",
            allow_blank=False,
            prompt="Play:",
        )

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        app.set_widget_availability()


class PlayButtonWidget(Widget):
    # pylint: disable=C0115, C0116
    def compose(self) -> ComposeResult:
        yield Button(">")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # pylint: disable=W0613
        app.play()


class PlayingFingerWidget(Widget):
    # pylint: disable=C0115, C0116
    playing_finger: reactive[str] = reactive("", recompose=True)

    def compose(self) -> ComposeResult:
        yield Label("Finger")
        yield Digits(self.playing_finger)

    def on_mount(self) -> None:
        self.visible = False


class InteractiveFretboardUi(FretboardUi):
    """Extended FretboardUi with interaction functionality"""

    # pylint: disable=C0116
    def on_fretboard_ui_cell_pluck(self, message: FretboardUiCell.Pluck) -> None:
        app.play_fret_note(message.string, message.fret)

    def on_fretboard_ui_cell_enter(self, message: FretboardUiCell.Enter) -> None:
        cell = self.fretboard_ui_cell(message.string, message.fret)
        cell.add_class("mouse-on-cell")

    def on_fretboard_ui_cell_leave(self, message: FretboardUiCell.Leave) -> None:
        cell = self.fretboard_ui_cell(message.string, message.fret)
        cell.remove_class("mouse-on-cell")


class InteractiveFretboardApp(App):
    """The textual application. Manages UI and logic."""

    CSS_PATH = "interactive_fretboard_app.tcss"
    TITLE = "Geekar"
    BINDINGS = [
        ("p", "play", "Play"),
    ]

    def __init__(
        self, key_name: str = DEFAULT_KEY_NAME, key_type: str = DEFAULT_KEY_TYPE
    ):
        self.key_name: str = key_name
        self.key_type: str = key_type
        self.tuning: str = "Standard"
        self.active_patterns: list = []
        self.fret_content: str = ""
        self.degree: int = 1
        self.midi_synth = MidiSynth()
        self.sequencer = None
        self.instrument: int = 27
        super().__init__()

    def _add_cell_content(
        self,
        cell,
        m21_cell_diatonic_name: str,
        active_key: Key,
        roman_pitches: dict,
    ):
        cell_pitch_name = geekar_types.geekar_pitch_name(m21_cell_diatonic_name)
        cell_degree = active_key.getScaleDegreeFromPitch(
            Pitch(m21_cell_diatonic_name),
        )
        cell_degree_accidental = (
            "b"
            if (active_key.mode == "minor" and cell_degree in MINOR_KEY_FLAT_DEGREES)
            else ""
        )
        if self.fret_content == "sn":
            cell.cell_text = f" {cell_pitch_name} "
        elif self.fret_content == "dg":
            cell_degree_text = f"{cell_degree_accidental}{str(cell_degree)}"
            cell.cell_text = f" {(
                cell_degree_text if m21_cell_diatonic_name != self.key_name else "R"
            )} "
        elif self.fret_content == "dt":
            cell.cell_text = f" {(
                cell_pitch_name
                if m21_cell_diatonic_name in roman_pitches[app.degree]
                else cell.default_cell_text())} "

    def _paint_groups(self, cell, groups: set):
        if not groups:
            return

        if len(groups) > 2:
            raise RuntimeError("Cannot paint more than 2 groups")

        sorted_groups = sorted(groups)
        cell.add_class(str(CAGED_BACKGROUND_LEGEND.get(sorted_groups[0])))

        if len(groups) == 2:
            cell.add_class(str(CAGED_TEXT_COLOR_LEGEND.get(sorted_groups[1])))
            # cell_content = self.query_one(f"#cell-content-{cell.string}-{cell.fret}")
            # cell_content.styles.background = 'blue'

    def _decorate_cell(
        self,
        fretboard,
        string_num: int,
        fret_num: int,
        m21_key_name: str,
        active_key: Key,
        roman_pitches: dict,
        caged_notes: list,
    ):
        cell = fretboard.fretboard_ui_cell(string_num, fret_num)

        m21_cell_diatonic_name = geekar_types.diatonic_pitch_name(
            string_num, fret_num, app.tuning, active_key
        )

        if not m21_cell_diatonic_name or (
            m21_cell_diatonic_name
            and self.key_type in ("MP", "mp")
            and not geekar_types.in_pentatonic(
                active_key, m21_cell_diatonic_name, self.key_type
            )
        ):
            return

        cell_groups = (
            [
                grouped_note.group
                for grouped_note in caged_notes
                if (
                    (grouped_note.group in self.active_patterns)
                    and (grouped_note.fret_note.string == string_num)
                    and (grouped_note.fret_note.fret == fret_num)
                )
            ]
            if self.tuning == "Standard" and self.active_patterns
            else []
        )

        self._add_cell_content(cell, m21_cell_diatonic_name, active_key, roman_pitches)

        if cell_groups:
            self._paint_groups(cell, set(cell_groups))
        else:
            cell.add_class("diatonic-note-fretboard-cell")

        if m21_cell_diatonic_name == m21_key_name:
            cell.add_class("root-note")

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            with Collapsible(collapsed=False, title="Settings", classes="collapsible"):
                with Grid(classes="form-grid"):
                    yield Label("Scale:")
                    yield KeyTypeSelectorWidget(id="key-type-selector-widget")
                    yield Label("Key:")
                    yield KeyNameSelectorWidget(id="key-name-selector-widget")
                    yield Label("Instrument:")
                    yield InstrumentSelectorWidget(id="instrument-selector-widget")
                    yield Label("Tuning:")
                    yield TuningSelectorWidget(id="tuning-selector-widget")
                    yield Label("Fret content:")
                    yield FretContentSelectorWidget(id="fret-content-selector-widget")
                    yield Label("Degree:", id="degree-selector-label")
                    yield DegreeSelectorWidget(id="degree-selector-widget")
            with Collapsible(collapsed=True, title="CAGED", classes="collapsible"):
                yield PatternSetWidget()
            with Collapsible(collapsed=True, title="Play", classes="collapsible"):
                with Grid(classes="form-grid"):
                    yield Label("Type:")
                    yield PlayTypeSelectorWidget(id="play-type-selector-widget")
                    yield Label("BPM:")
                    yield Input(
                        id="bpm-input",
                        placeholder="60",
                        value="60",
                        type="integer",
                        validators=[Number(minimum=40, maximum=120)],
                    )
                    yield Static()
                    yield PlayButtonWidget(id="play-button-widget")
        yield PlayingFingerWidget()
        yield InteractiveFretboardUi()
        yield Footer()

    def on_mount(self) -> None:
        # pylint: disable=C0116
        self.theme = "textual-light"

    @staticmethod
    def play_fret_note(string_num: int, fret_num: int):
        """Plays the pitch on the string/fret provided"""
        cell_pitch = geekar_types.fret_note_pitch(string_num, fret_num, app.tuning)
        geekar_pitch = geekar_types.geekar_pitch_name(cell_pitch.nameWithOctave)
        midi_note = note_to_midi(geekar_pitch)
        logger.debug(
            "Playing string_num: %s, fret_num: %s, cell_pitch: %s geekar_pitch: %s, midi_note: %s",
            string_num,
            fret_num,
            cell_pitch,
            geekar_pitch,
            midi_note,
        )
        app.midi_synth.note_on(midi_note)
        sleep(0.5)
        app.midi_synth.note_off(midi_note)

    # def clear_widget_state(self):
    #     for pattern in app.active_patterns:
    #         switch = self.query_one(f"#{str.lower(pattern)}-pattern-switch", Switch)
    #         switch.toggle()

    def set_widget_availability(self):
        """Controls which which widgets should be available
        according to the application state"""
        degree_selector_widget = self.query_one("#degree-selector-widget")
        play_type_selector_widget = self.query_one("#play-type-selector-widget")
        bpm_input = app.query_one("#bpm-input", Input)
        pattern_set_widget = self.query_one(PatternSetWidget)
        play_type_selector = self.query_one("#play-type-selector", Select)
        play_button_widget = self.query_one("#play-button-widget")
        degree_selector_widget.disabled = app.fret_content != "dt"
        pattern_set_widget.disabled = app.tuning != "Standard"
        play_type_selector_widget.disabled = bool(app.sequencer)
        bpm_input.disabled = bool(app.sequencer)
        play_button_widget.disabled = play_type_selector.value == "s" and (
            (not app.key_name) or (app.tuning != "Standard")
        )

    def undecorate_fetboard(self, painting_classes: set):
        """Removes fretboard decoration. In general, it should be called
        each time options change and a before (re)decoration starts"""
        fretboard = self.query_one(FretboardUi)
        for string in range(1, fretboard.NUM_OF_STRINGS + 1):
            for fret in range(fretboard.num_of_frets):
                cell = fretboard.fretboard_ui_cell(string, fret)
                cell.remove_class(*painting_classes)
                # cell.cell_text = FretboardUiCell.DEFAULT_CELL_TEXT if fret != 0 else ""
                cell.cell_text = cell.default_cell_text()

    def decorate_fretboard(self):
        """Manages fretboard decoration. It should be called when options
        (e.g. key, fret content, etc.) are changed"""
        fretboard = self.query_one(FretboardUi)

        pattern_background_classes = {
            pattern_class for _, pattern_class in CAGED_BACKGROUND_LEGEND.items()
        }
        pattern_text_color_classes = {
            pattern_class for _, pattern_class in CAGED_TEXT_COLOR_LEGEND.items()
        }
        painting_classes = (
            pattern_background_classes
            | pattern_text_color_classes
            | {"playing-fretboard-cell", "diatonic-note-fretboard-cell", "root-note"}
        )

        self.undecorate_fetboard(painting_classes)

        if not self.key_name:
            return

        m21_key_name = geekar_types.m21_pitch_name(self.key_name)

        active_key = (
            Key(m21_key_name)
            if self.key_type in ["M", "MP"]
            else Key(str.lower(m21_key_name))
        )

        caged = CagedSystem(self.key_name, self.key_type)
        caged_notes = caged.ascending_fret_notes()

        roman_pitches = geekar_types.roman_pitches(active_key)
        logger.debug("roman_pitches: %s", roman_pitches)
        for string_num in range(1, FretboardUi.NUM_OF_STRINGS + 1):
            for fret_num in range(FretboardUi.NUM_OF_FRETS):
                self._decorate_cell(
                    fretboard,
                    string_num,
                    fret_num,
                    m21_key_name,
                    active_key,
                    roman_pitches,
                    caged_notes,
                )

    def action_play(self):
        """Play action bound to application triggers metronome/scale play"""
        self.play()

    def play(self):
        """Manages playing type. It triggers
        metronome or scale playing."""
        play_type = str(app.query_one("#play-type-selector", Select).value)
        logger.debug("Play %s", play_type)
        if play_type == "s":
            self.play_scale()
        elif play_type == "m":
            self.play_metronome()
        else:
            raise RuntimeError(f"Uknown play type {play_type}")

        self.set_widget_availability()

    def play_scale(self):
        """Starts/stops scale simulation"""
        if not self.key_name:
            return

        caged = CagedSystem(self.key_name, self.key_type)
        caged_notes = caged.up_down_fret_notes()
        fretboard = app.query_one(FretboardUi)
        bpm_input = app.query_one("#bpm-input", Input)
        playing_fret_widget = app.query_one(PlayingFingerWidget)
        playing_fret_widget.visible = True

        def _clear_decorations():
            for scale_note in caged_notes:
                cell = fretboard.fretboard_ui_cell(
                    scale_note.fret_note.string, scale_note.fret_note.fret
                )
                cell.remove_class("mouse-on-cell")
            playing_fret_widget.visible = False

        def _stop_simulation():
            if self.sequencer:
                self.sequencer.delete()
                self.sequencer = None
            _clear_decorations()

        def _cleanup_simulation_callback(time, event, seq, data):
            # pylint: disable=W0613
            _clear_decorations()

            self.sequencer = None

        def _paint_playing_note_callback(time, event, seq, data):
            # pylint: disable=W0613
            note_index = int(data) if data else 0

            if note_index >= 1:
                prv_fret_note = caged_notes[note_index - 1].fret_note
                prv_cell = fretboard.fretboard_ui_cell(
                    prv_fret_note.string, prv_fret_note.fret
                )
                prv_cell.remove_class("mouse-on-cell")

            curr_fret_note = caged_notes[note_index].fret_note
            curr_cell = fretboard.fretboard_ui_cell(
                curr_fret_note.string, curr_fret_note.fret
            )
            curr_cell.add_class("mouse-on-cell")
            logger.debug("Painting cell %s", curr_cell)
            playing_fret_widget.playing_finger = str(curr_fret_note.fingering)

        def _schedule_simulation():
            self.sequencer = fluidsynth.Sequencer(use_system_timer=False)
            synth_id = self.sequencer.register_fluidsynth(app.midi_synth.synthesizer)
            now = self.sequencer.get_tick()
            tick_duration = int(60 / int(bpm_input.value) * 1000)

            clean_up_callback_id = self.sequencer.register_client(
                "clean_up_callback", _cleanup_simulation_callback
            )

            for i in range(4):
                self.sequencer.note_on(
                    now + (i * tick_duration),
                    absolute=False,
                    channel=0,
                    key=note_to_midi("A2"),
                    velocity=100,
                    dest=synth_id,
                )

            for note_index, scale_note in enumerate(caged_notes):
                paint_callback_id = self.sequencer.register_client(
                    "paint_callback", _paint_playing_note_callback, data=note_index
                )
                note_pitch = geekar_types.fret_note_pitch(
                    scale_note.fret_note.string, scale_note.fret_note.fret, app.tuning
                )
                geekar_pitch = geekar_types.geekar_pitch_name(note_pitch.nameWithOctave)
                midi_note = note_to_midi(geekar_pitch)
                self.sequencer.note_on(
                    now + ((note_index + 4) * tick_duration),
                    absolute=False,
                    channel=0,
                    key=midi_note,
                    velocity=100,
                    dest=synth_id,
                )
                self.sequencer.timer(
                    now + ((note_index + 4) * tick_duration), dest=paint_callback_id
                )

            self.sequencer.timer(
                now + ((len(caged_notes) + 4) * tick_duration),
                dest=clean_up_callback_id,
            )

        # If a sequencer exists, simulation is in progress. User has opted to stop it.
        if self.sequencer:
            _stop_simulation()
            return

        _schedule_simulation()

    def play_metronome(self):
        """Starts/stops the metronome"""
        bpm_input = app.query_one("#bpm-input", Input)

        def _stop_metronome():
            if self.sequencer:
                self.sequencer.delete()
                self.sequencer = None
                self.midi_synth.select_midi_program(app.instrument)

        def _schedule_metronome():
            self.midi_synth.select_midi_program(115)  # 27, 38, 115, 117
            self.sequencer = fluidsynth.Sequencer(use_system_timer=False)
            synth_id = self.sequencer.register_fluidsynth(app.midi_synth.synthesizer)
            now = self.sequencer.get_tick()
            tick_duration = int(60 / int(bpm_input.value) * 1000)

            for i in range(10000):
                self.sequencer.note_on(
                    now + (i * tick_duration),
                    absolute=False,
                    channel=0,
                    key=note_to_midi("A2"),
                    velocity=120,
                    dest=synth_id,
                )

        # If a sequencer exists, metronome is playing. User has opted to stop it.
        if self.sequencer:
            _stop_metronome()
            return

        _schedule_metronome()


app = InteractiveFretboardApp()


def main():
    """Executes the application"""
    app.run()
