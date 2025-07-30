# SPDX-FileCopyrightText: 2025 Dimitris Kardarakos
# SPDX-License-Identifier: AGPL-3.0-only


from music21.key import Key
from music21.tablature import FretNote
from music21.scale import MinorScale
from geekar.geekar_types import (
    geekar_pitch_name,
    GroupedFretNote,
    diatonic_pitch_name,
    in_pentatonic,
    m21_pitch_name,
)


class CagedSystem:
    """Defines the CAGED system patterns for several scales"""

    def __init__(self, key_name: str, scale_type: str):
        self.key_name = key_name
        self.scale_type = scale_type

    def c_major_system(self, offset: int):
        """Returns a list of tuples with this format: (string_number, fret_number, finger)
        for the C pattern of the CAGED system. Offset is the fret of the first note of the
        pattern (0 means open string).
        """
        return [
            (6, offset + 0, 0 if offset == 0 else 1),  # Start: C, Db, D
            (6, offset + 1, 1 if offset == 0 else 2),
            (6, offset + 3, 3 if offset == 0 else 4),
            (5, offset + 0, 0 if offset == 0 else 1),
            (5, offset + 2, 2 if offset == 0 else 3),
            (5, offset + 3, 3 if offset == 0 else 4),
            (4, offset + 0, 0 if offset == 0 else 1),
            (4, offset + 2, 2 if offset == 0 else 3),
            (4, offset + 3, 3 if offset == 0 else 4),
            (3, offset + 0, 0 if offset == 0 else 1),
            (3, offset + 2, 2 if offset == 0 else 3),
            (2, offset + 0, 0 if offset == 0 else 1),
            (2, offset + 1, 1 if offset == 0 else 2),
            (2, offset + 3, 3 if offset == 0 else 4),
            (1, offset + 0, 0 if offset == 0 else 1),
            (1, offset + 1, 1 if offset == 0 else 2),
            (1, offset + 3, 3 if offset == 0 else 4),
        ]

    def a_major_system(self, offset: int):
        """Returns a list of tuples with this format:
        (string_number, fret_number, finger)
        for the A pattern of the CAGED system
        """
        return [
            (6, offset + 1, 1),  # if offset == 0 else 2),  # Start: ["Bb", "B"]
            (6, offset + 3, 3),  # if offset == 0 else 4),
            (5, offset + 0, 0 if offset == 0 else 1),
            (5, offset + 1, 1 if offset == 0 else 2),
            (5, offset + 3, 3 if offset == 0 else 4),
            (4, offset + 0, 0 if offset == 0 else 1),
            (4, offset + 1, 1 if offset == 0 else 2),
            (4, offset + 3, 3 if offset == 0 else 4),
            (3, offset + 0, 0 if offset == 0 else 1),
            (3, offset + 2, 2 if offset == 0 else 3),
            (3, offset + 3, 3 if offset == 0 else 4),
            (2, offset + 1, 1),
            (2, offset + 3, 3),
            (2, offset + 4, 4),
            (1, offset + 1, 1 if offset == 2 else 2),
            (1, offset + 3, 3 if offset == 2 else 4),
        ]

    def g_major_system(self, offset: int):
        """Returns a list of tuples with this format:
        (string_number, fret_number, finger)
        for the G pattern of the CAGED system
        """
        return [
            (6, offset + 0, 1),  # Start: Ab, A
            (6, offset + 2, 3),
            (6, offset + 3, 4),
            (5, offset + 0, 1),
            (5, offset + 2, 3),
            (5, offset + 3, 4),
            (4, offset + 0, 1),
            (4, offset + 2, 3),
            (3, offset - 1, 0 if offset == 1 else 1),
            (3, offset + 0, 1 if offset == 1 else 2),
            (3, offset + 2, 3 if offset == 1 else 4),
            (2, offset + 0, 1),
            (2, offset + 1, 2),
            (2, offset + 3, 4),
            (1, offset + 0, 1),
            (1, offset + 2, 3),
            (1, offset + 3, 4),
        ]

    def e_major_system(self, offset: int):
        """Returns a list of tuples with this format:
        (string_number, fret_number, finger)
        for the E pattern of the CAGED system
        """
        return [
            (6, offset + 0, 0 if offset == 0 else 1),  # Starts: ["F", "Gb", "G"]),
            (6, offset + 1, 1 if offset == 0 else 2),
            (6, offset + 3, 3 if offset == 0 else 4),
            (5, offset + 0, 0 if offset == 0 else 1),
            (5, offset + 1, 1 if offset == 0 else 2),
            (5, offset + 3, 3 if offset == 0 else 4),
            (4, offset + 0, 0 if offset == 0 else 1),
            (4, offset + 2, 2 if offset == 0 else 3),
            (4, offset + 3, 3 if offset == 0 else 4),
            (3, offset + 0, 0 if offset == 0 else 1),
            (3, offset + 2, 2 if offset == 0 else 3),
            (3, offset + 3, 3 if offset == 0 else 4),
            (2, offset + 1, 1 if offset == 0 else 2),
            (2, offset + 3, 3 if offset == 0 else 4),
            (1, offset + 0, 0 if offset == 0 else 1),
            (1, offset + 1, 1 if offset == 0 else 2),
            (1, offset + 3, 3 if offset == 0 else 4),
        ]

    def d_major_system(self, offset: int):
        """Returns a list of tuples with this format:
        (string_number, fret_number, finger)
        for the D pattern of the CAGED system
        """
        return [
            (6, offset + 0, 1),  # Start of: Eb, E
            (6, offset + 2, 3),
            (6, offset + 3, 4),
            (5, offset + 0, 1),
            (5, offset + 2, 3),
            (4, offset - 1, 0 if offset == 1 else 1),
            (4, offset + 0, 1 if offset == 1 else 2),
            (4, offset + 2, 3 if offset == 1 else 4),
            (3, offset - 1, 0 if offset == 1 else 1),
            (3, offset + 0, 1 if offset == 1 else 2),
            (3, offset + 2, 3 if offset == 1 else 4),
            (2, offset + 0, 1),
            (2, offset + 2, 3),
            (2, offset + 3, 4),
            (1, offset + 0, 1),
            (1, offset + 2, 3),
            (1, offset + 3, 4),
        ]

    MAJOR_KEY_SYSTEM_MAP = {
        "C": {
            "starting_system": "C",
            "offset": 0,
        },
        "C#": {"starting_system": "C", "offset": 1},
        "Db": {"starting_system": "C", "offset": 1},
        "D": {
            "starting_system": "C",
            "offset": 2,
        },
        "D#": {"starting_system": "D", "offset": 1},
        "Eb": {"starting_system": "D", "offset": 1},
        "E": {"starting_system": "D", "offset": 2},
        "F": {"starting_system": "E", "offset": 0},
        "F#": {"starting_system": "E", "offset": 1},
        "Gb": {"starting_system": "E", "offset": 1},
        "G": {"starting_system": "E", "offset": 2},
        "G#": {"starting_system": "G", "offset": 1},
        "Ab": {"starting_system": "G", "offset": 1},
        "A": {"starting_system": "G", "offset": 2},
        "A#": {"starting_system": "G", "offset": 2},
        "Bb": {"starting_system": "A", "offset": 0},
        "B": {"starting_system": "A", "offset": 1},
        "Cb": {"starting_system": "A", "offset": 1},
    }

    CAGED_SYSTEMS = {
        "C": c_major_system,
        "A": a_major_system,
        "G": g_major_system,
        "E": e_major_system,
        "D": d_major_system,
    }

    TRANSITIONS = {
        ("C", "A"): {"distance": 2},
        ("A", "G"): {"distance": 3},
        ("G", "E"): {"distance": 2},
        ("E", "D"): {"distance": 3},
        ("D", "C"): {"distance": 2},
    }

    def _transition_tuples(
        self, from_system: str, from_ascending: bool, to_system: str, offset: int
    ):
        transition_tuples = {
            ("E", False, "D"): [(6, offset + 1, 1, "E")],
            ("E", True, "D"): [(1, offset + 5, 1, "D")],
            ("C", False, "A"): [(6, offset + 1, 1, "C")],
            ("A", True, "G"): [(1, offset + 5, 1, "G")],
        }

        return (
            transition_tuples[(from_system, from_ascending, to_system)]
            if (from_system, from_ascending, to_system) in transition_tuples
            else []
        )

    def ordered_tuples(self, offset: int, system_sequence: list) -> list[tuple]:
        """Creates a list of tuples based on the list of systems in the @system_sequence and
        @offset (the fret of the first note in the system)."""
        tuples: list[tuple] = []
        transition_distance = 0
        transition_tuples: list[tuple] = []
        for i, current_system in enumerate(system_sequence):
            system_method = self.CAGED_SYSTEMS[current_system]
            current_system_tuples = [
                t + (current_system,)
                for t in system_method(self, transition_distance + offset)
            ]
            tuples = (
                tuples
                + transition_tuples
                + (
                    current_system_tuples
                    if (i % 2 == 0)
                    else list(reversed(current_system_tuples))
                )
            )

            if i < (len(system_sequence) - 1):
                next_system = system_sequence[i + 1]
                transition_tuples = self._transition_tuples(
                    current_system,
                    (i % 2 == 0),
                    next_system,
                    offset + transition_distance,
                )
                transition_distance += self.TRANSITIONS[(current_system, next_system)][
                    "distance"
                ]
        return tuples

    def ascending_fret_notes(self) -> list[GroupedFretNote]:
        """Returns the ascending (low to high pitch) list of GroupedFretNote
        for the key of the CagedSystem"""
        if self.scale_type in ["M", "MP"]:
            key_of_major = self.key_name
        else:
            minor_scale = MinorScale(tonic=self.key_name)
            major_scale = minor_scale.getRelativeMajor()
            major_tonic = major_scale.tonic
            if major_tonic:
                key_of_major = geekar_pitch_name(major_tonic.name)
            else:
                raise RuntimeError("Cannot calculate relative major")

        system_map = self.MAJOR_KEY_SYSTEM_MAP[key_of_major]

        caged_str = "CAGED"
        index_of_start = caged_str.index(str(system_map["starting_system"]))
        system_sequence = list(caged_str[index_of_start:]) + list(
            caged_str[:index_of_start]
        )

        system_tuples = self.ordered_tuples(
            int(str(system_map["offset"])), system_sequence
        )

        notes_list = [
            GroupedFretNote(
                fret_note=FretNote(string=st[0], fret=st[1], fingering=st[2]),
                group=st[3],
            )
            for st in system_tuples
        ]

        if self.scale_type in ["MP", "mp"]:
            notes_list = self._pentatonic_notes(notes_list)

        return notes_list

    def _pentatonic_notes(self, notes_list: list) -> list:
        active_key = (
            Key(self.key_name)
            if self.scale_type == "MP"
            else Key(str.lower(self.key_name))
        )

        # notes_list = [
        #     gfn
        #     for gfn in notes_list
        #     if pentatonic_pitch_name(
        #         active_key,
        #         diatonic_pitch_name(
        #             gfn.fret_note.string, gfn.fret_note.fret, "Standard", active_key
        #         ),
        #         self.scale_type,
        #     )
        # ]
        #
        notes_list = [
            gfn
            for gfn in notes_list
            if in_pentatonic(
                active_key,
                diatonic_pitch_name(
                    gfn.fret_note.string, gfn.fret_note.fret, "Standard", active_key
                ),
                self.scale_type,
            )
        ]

        prev_note = None
        for _, note in enumerate(notes_list):
            if (
                prev_note
                and (prev_note.fret_note.string == note.fret_note.string)
                and (prev_note.fret_note.fret == note.fret_note.fret)
            ):
                notes_list.remove(note)
            prev_note = note

        return notes_list

    def up_down_fret_notes(self) -> list[GroupedFretNote]:
        """Returns the ascending (low to high pitch) and descending (high to low)
        list of GroupedFretNote for the key of the CagedSystem"""

        up_notes_list = self.ascending_fret_notes()
        down_notes_list = list(reversed(up_notes_list))[1:]
        active_key = (
            Key(self.key_name)
            if self.scale_type in ["M", "MP"]
            else Key(str.lower(self.key_name))
        )

        up_pitch_names = [
            diatonic_pitch_name(
                gfn.fret_note.string, gfn.fret_note.fret, "Standard", active_key
            )
            for gfn in up_notes_list
            if gfn.fret_note.string and gfn.fret_note.fret
        ]
        index_of_key_pitch = up_pitch_names.index(m21_pitch_name(self.key_name))

        return (
            up_notes_list + down_notes_list + up_notes_list[1 : index_of_key_pitch + 1]
        )
