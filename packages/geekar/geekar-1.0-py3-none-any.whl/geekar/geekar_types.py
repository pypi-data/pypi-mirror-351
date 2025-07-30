# SPDX-FileCopyrightText: 2025 Dimitris Kardarakos
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import dataclass
from music21.pitch import Pitch
from music21.key import Key
from music21.tablature import FretNote

TUNING = {
    "Standard": {
        6: Pitch("E2"),
        5: Pitch("A2"),
        4: Pitch("D3"),
        3: Pitch("G3"),
        2: Pitch("B3"),
        1: Pitch("E4"),
    },
    "Drop D": {
        6: Pitch("D2"),
        5: Pitch("A2"),
        4: Pitch("D3"),
        3: Pitch("G3"),
        2: Pitch("B3"),
        1: Pitch("E4"),
    },
}

MAJOR_PENTATONIC_DEGREES = [1, 2, 3, 5, 6]

MINOR_PENTATONIC_DEGREES = [1, 3, 4, 5, 7]


@dataclass
class GroupedFretNote:
    """A music21 FretNote for CAGED"""

    fret_note: FretNote
    group: str


def enharmonic_pitch_name(pitch_name: str) -> str:
    """Returns the enharmonic pitch name"""

    enharmonic_pitch = Pitch(pitch_name).getEnharmonic()

    return enharmonic_pitch.name if enharmonic_pitch else ""


def geekar_pitch_name(pitch_name: str) -> str:
    """Returns the pitch name replacing - with b"""

    return pitch_name.replace("-", "b")


def m21_pitch_name(pitch_name: str) -> str:
    """Returns the pitch name replacing - with b"""

    return pitch_name.replace("b", "-")


def fret_note_pitch(string: int, fret: int, tuning: str) -> Pitch:
    """Returns the Pitch of a specific location on the fret board
    for the @tuning provided"""
    # logger.debug("string: %s, fret: %s", string, fret)
    open_pitch_set = TUNING[tuning]
    open_pitch = open_pitch_set[string]
    note_pitch = open_pitch.transpose(fret)
    # logger.debug("note_pitch %s", note_pitch)
    return note_pitch


def diatonic_pitch_name(
    string_num: int, fret_num: int, tuning: str, active_key: Key
) -> str:
    """Returns the name of the pitch of the fret note with string_num, fret_num
    on the scale provided. If not a diatonic pitch is found, it returns an empty string.
    """

    pitch = fret_note_pitch(string_num, fret_num, tuning)
    enharmonics = pitch.getAllCommonEnharmonics()
    scale_pitch_names = [p.name for p in active_key.pitches]

    if pitch.name in scale_pitch_names:
        return pitch.name

    for en_pitch in enharmonics:
        if en_pitch.name in scale_pitch_names:
            return en_pitch.name

    return ""


def in_pentatonic(active_key: Key, diatonic_name: str, scale_type: str) -> bool:
    """Returns true if the @diatonic_name note is in the pentatonic scale given"""
    degree = active_key.getScaleDegreeFromPitch(
        Pitch(diatonic_name), comparisonAttribute="pitchClass"
    )
    pentatonic_degrees = (
        MAJOR_PENTATONIC_DEGREES if scale_type == "MP" else MINOR_PENTATONIC_DEGREES
    )

    return degree in pentatonic_degrees


def roman_pitches(active_key: Key) -> dict:
    """Returns a dictionary with the pitch names of each defree of the @active_key.
    E.g., for C key, it returns:
    {
        1: ['C', 'E', 'G'], 2: ['D', 'F', 'A'], 3: ['E', 'G', 'B'], 4: ['F', 'A', 'C'],
        5: ['G', 'B', 'D'], 6: ['A', 'C', 'E'],7: ['B', 'D', 'F#']
    }"""
    pitches = {}
    for d in range(1, 8):
        roman = active_key.romanNumeral(d)
        pitches[d] = roman.pitchNames
    return pitches
