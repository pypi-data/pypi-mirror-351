# SPDX-FileCopyrightText: 2025 Dimitris Kardarakos, 2023 Elias Dorneles
# SPDX-License-Identifier: MIT


"""
MidiSynth class for playing midi notes.
"""

import os
import fluidsynth
from xdg.BaseDirectory import load_data_paths

DEFAULT_SOUND_FONT = "default.sf2"
# E.g., MS Basic.sf3", "FluidR3_GM.sf2", "FluidR3_GS.sf2", "GeneralUser_GS_v1.471.sf2"

GUITAR_MIDI_INSTRUMENTS = {
    "Acoustic Guitar (nylon)": 24,
    "Acoustic Guitar (steel)": 25,
    "Electric Guitar (jazz)": 26,
    "Electric Guitar (clean)": 27,
    "Electric Guitar (muted)": 28,
    "Overdriven Guitar": 29,
    "Distortion Guitar": 30,
    "Guitar Harmonics": 31,
    "Acoustic Bass": 32,
    "Electric Bass (finger)": 33,
    "Electric Bass (pick)": 34,
    "Fretless Bass": 35,
    "Slap Bass 1": 36,
    "Slap Bass 2": 37,
    "Synth Bass 1": 38,
    "Synth Bass 2": 39,
    "Guitar Fret Noise": 120,
}

GENERAL_MIDI_INSTRUMENTS = [
    "Acoustic Grand Piano",
    "Bright Acoustic Piano",
    "Electric Grand Piano",
    "Honky-tonk Piano",
    "Electric Piano 1",
    "Electric Piano 2",
    "Harpsichord",
    "Clavi",
    "Celesta",
    "Glockenspiel",
    "Music Box",
    "Vibraphone",
    "Marimba",
    "Xylophone",
    "Tubular Bells",
    "Dulcimer",
    "Drawbar Organ",
    "Percussive Organ",
    "Rock Organ",
    "Church Organ",
    "Reed Organ",
    "Accordion",
    "Harmonica",
    "Tango Accordion",
    "Acoustic Guitar (nylon)",
    "Acoustic Guitar (steel)",
    "Electric Guitar (jazz)",
    "Electric Guitar (clean)",
    "Electric Guitar (muted)",
    "Overdriven Guitar",
    "Distortion Guitar",
    "Guitar Harmonics",
    "Acoustic Bass",
    "Electric Bass (finger)",
    "Electric Bass (pick)",
    "Fretless Bass",
    "Slap Bass 1",
    "Slap Bass 2",
    "Synth Bass 1",
    "Synth Bass 2",
    "Violin",
    "Viola",
    "Cello",
    "Contrabass",
    "Tremolo Strings",
    "Pizzicato Strings",
    "Orchestral Harp",
    "Timpani",
    "String Ensemble 1",
    "String Ensemble 2",
    "Synth Strings 1",
    "Synth Strings 2",
    "Choir Aahs",
    "Voice Oohs",
    "Synth Choir",
    "Orchestra Hit",
    "Trumpet",
    "Trombone",
    "Tuba",
    "Muted Trumpet",
    "French Horn",
    "Brass Section",
    "Synth Brass 1",
    "Synth Brass 2",
    "Soprano Sax",
    "Alto Sax",
    "Tenor Sax",
    "Baritone Sax",
    "Oboe",
    "English Horn",
    "Bassoon",
    "Clarinet",
    "Piccolo",
    "Flute",
    "Recorder",
    "Pan Flute",
    "Blown Bottle",
    "Shakuhachi",
    "Whistle",
    "Ocarina",
    "Lead 1 (square)",
    "Lead 2 (sawtooth)",
    "Lead 3 (calliope)",
    "Lead 4 (chiff)",
    "Lead 5 (charang)",
    "Lead 6 (voice)",
    "Lead 7 (fifths)",
    "Lead 8 (bass + lead)",
    "Pad 1 (new age)",
    "Pad 2 (warm)",
    "Pad 3 (polysynth)",
    "Pad 4 (choir)",
    "Pad 5 (bowed)",
    "Pad 6 (metallic)",
    "Pad 7 (halo)",
    "Pad 8 (sweep)",
    "FX 1 (rain)",
    "FX 2 (soundtrack)",
    "FX 3 (crystal)",
    "FX 4 (atmosphere)",
    "FX 5 (brightness)",
    "FX 6 (goblins)",
    "FX 7 (echoes)",
    "FX 8 (sci-fi)",
    "Sitar",
    "Banjo",
    "Shamisen",
    "Koto",
    "Kalimba",
    "Bagpipe",
    "Fiddle",
    "Shanai",
    "Tinkle Bell",
    "Agogo",
    "Steel Drums",
    "Woodblock",
    "Taiko Drum",
    "Melodic Tom",
    "Synth Drum",
    "Reverse Cymbal",
    "Guitar Fret Noise",
    "Breath Noise",
    "Seashore",
    "Bird Tweet",
    "Telephone Ring",
    "Helicopter",
    "Applause",
    "Gunshot",
]


# https://www.midi.org/specifications-old/item/gm-level-1-sound-set
_INSTRUMENT_FAMILIES = [
    "Piano",
    "Chromatic Percussion",
    "Organ",
    "Guitar",
    "Bass",
    "Strings",
    "Ensemble",
    "Brass",
    "Reed",
    "Pipe",
    "Synth Lead",
    "Synth Pad",
    "Synth Effects",
    "Ethnic",
    "Percussive",
    "Sound Effects",
]


def gm_family(program_id: int) -> str:
    """Return the instrument family number"""
    return _INSTRUMENT_FAMILIES[program_id // 8]


def note_to_midi(note: str) -> int:
    """
    Convert a note string to a midi note value.
    >>> note_to_midi("C4")
    60
    >>> note_to_midi("C#4")
    61
    """
    octave = int(note[-1])
    accidental_offset = 0
    if note[1] == "#":
        accidental_offset = 1
    elif note[1] == "b":
        accidental_offset = -1

    return 12 * (octave + 1) + "C D EF G A B".index(note[:1]) + accidental_offset


class MidiSynth:
    """Provides a synthesizer to play midi notes"""

    def __init__(self, soundfont_name=None):
        self.synthesizer = fluidsynth.Synth()
        self.synthesizer.start()
        self.soundfont_id = self.load_soundfont(soundfont_name or DEFAULT_SOUND_FONT)
        self.select_midi_program(0)

    def load_soundfont(self, name):
        """Loads the soundfont given"""

        soundfont_dir = ""

        for soundfont_dir in load_data_paths("soundfonts"):
            if soundfont_dir:
                break

        if not soundfont_dir:
            raise RuntimeError(
                "Please install soundfonts using the package manager of your distribution"
            )

        soundfont_path = os.path.join(soundfont_dir, name)

        if not os.path.exists(soundfont_path):
            raise FileNotFoundError("Soundfont file not found")

        return self.synthesizer.sfload(soundfont_path)

    def select_midi_program(self, program_id, channel=0, bank_id=0):
        """Selects a midi program (instrument)"""
        self.synthesizer.program_select(
            channel,
            self.soundfont_id,
            bank_id,
            program_id,
        )

        # pylint: disable=C0116

    def note_on(self, note_value, channel=0, velocity=100):
        self.synthesizer.noteon(channel, note_value, velocity)

    def note_off(self, note_value, channel=0):
        self.synthesizer.noteoff(channel, note_value)

    def set_sustain(self, value, channel=0):
        self.synthesizer.cc(channel, 64, value)

    def set_volume(self, value, channel=0):
        self.synthesizer.cc(channel, 7, value)

    def set_chorus(self, value, channel=0):
        self.synthesizer.cc(channel, 93, value)

    def set_reverb(self, value, channel=0):
        self.synthesizer.cc(channel, 91, value)

    def get_volume(self, channel=0) -> int:
        return self.synthesizer.get_cc(channel, 7)

    def step_volume(self, channel: int = 0, step: int = 1):
        self.set_volume(self.get_volume(channel) + step, channel)
