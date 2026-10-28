"""Unit tests for midi_analysis. These run under plain CPython or Blender."""

import tempfile
import unittest
from pathlib import Path

from midi_analysis.MidiData import MidiData, NotSupportedException
from midi_analysis.MidiEvents import (
    ControllerEvent,
    KeySignatureEvent,
    NoteOnEvent,
    PitchBendEvent,
    ProgramChangeEvent,
    ChannelAftertouchEvent,
    SetTempoEvent,
    TextEvent,
    TimeSignatureEvent,
)
from midi_analysis.MidiParser import MidiParserException
from midi_analysis.Note import Note
from midi_analysis.Util import Util

from tests import midi_builder as mb

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "piano_format1.mid"


def load(path):
    data = MidiData(str(path))
    try:
        data.event_decoder.close()
    except Exception:
        pass
    return data


def note_rows(track):
    return [
        (note.pitch, note.velocity, note.channel, round(note.start_time, 3), round(note.end_time, 3))
        for note in track.notes
    ]


class MidiBuilderTests(unittest.TestCase):
    def test_vlq_boundaries(self):
        self.assertEqual(mb.vlq(0), b"\x00")
        self.assertEqual(mb.vlq(127), b"\x7f")
        self.assertEqual(mb.vlq(128), b"\x81\x00")
        self.assertEqual(mb.vlq(480), b"\x83\x60")
        self.assertEqual(mb.vlq(100000), bytes((0x86, 0x8D, 0x20)))

    def test_var_len_round_trip(self):
        for value in (0, 1, 127, 128, 480, 16383, 100000):
            self.assertEqual(Util.var_len_val(mb.vlq(value)), value)


class FormatTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def path(self, name):
        return Path(self.tmp.name) / name

    def test_format1_multiple_tracks_tempo_and_time_signature(self):
        data = load(mb.build_piano_format1(self.path("piano.mid")))
        self.assertEqual(data.format, 1)
        self.assertEqual(data.num_tracks, 4)
        self.assertTrue(data.is_ticks_per_beat)
        self.assertEqual(data.ticks_per_beat, 480)
        self.assertEqual(data.get_num_tracks(), 4)

        tempo_track = data.get_track(0)
        self.assertEqual(tempo_track.name, "Tempo")
        self.assertEqual(tempo_track.notes, [])
        tempos = [event for event in tempo_track.events if isinstance(event, SetTempoEvent)]
        self.assertEqual([event.tempo for event in tempos], [mb.TEMPO_120])
        signatures = [event for event in tempo_track.events if isinstance(event, TimeSignatureEvent)]
        self.assertEqual(
            [(sig.numerator, sig.denominator, sig.beats_per_tick, sig.thirty_second_notes_per_beat)
             for sig in signatures],
            [(4, 4, 1, 8), (3, 8, 1, 8)],
        )
        keys = [event for event in tempo_track.events if isinstance(event, KeySignatureEvent)]
        self.assertEqual(len(keys), 1)
        self.assertTrue(keys[0].major_key)
        self.assertTrue(keys[0].sharp_key)
        self.assertEqual(keys[0].number_of_accidentals, 2)
        texts = [event.text for event in tempo_track.events if isinstance(event, TextEvent)]
        self.assertIn("piano study", texts)

        self.assertEqual(
            note_rows(data.get_track(1)),
            [
                (60, 100, 0, 0.0, 500.0),
                (64, 80, 0, 0.0, 500.0),
                (67, 127, 0, 500.0, 750.0),
                (60, 40, 0, 1000.0, 1500.0),
            ],
        )
        bass = data.get_track(2)
        self.assertEqual(bass.name, "Bass")
        self.assertEqual(note_rows(bass), [(36, 90, 0, 0.0, 2000.0)])
        controllers = [event for event in bass.events if isinstance(event, ControllerEvent)]
        self.assertEqual([(event.controller_type, event.value, round(event.start_time, 3)) for event in controllers],
                         [(7, 100, 0.0), (7, 20, 500.0)])
        self.assertEqual(controllers[0].controller_type_string(), "Main Volume")
        bends = [event for event in bass.events if isinstance(event, PitchBendEvent)]
        self.assertEqual(bends[0].relative_bend_amount(), 256)
        programs = [event for event in bass.events if isinstance(event, ProgramChangeEvent)]
        self.assertEqual(programs[0].program_number, 33)
        self.assertEqual(data.get_track(3).name, "Empty")
        self.assertEqual(data.get_track(3).notes, [])

    def test_committed_format1_fixture(self):
        self.assertTrue(FIXTURE.is_file(), FIXTURE)
        data = load(FIXTURE)
        self.assertEqual(data.format, 1)
        self.assertEqual(note_rows(data.get_track(1))[0], (60, 100, 0, 0.0, 500.0))
        self.assertEqual(len(data.get_track(1).notes), 4)
        self.assertEqual(len(data.get_track(3).notes), 0)

    def test_format0_tempo_change(self):
        data = load(mb.build_format0(self.path("fmt0.mid")))
        self.assertEqual(data.format, 0)
        self.assertEqual(data.get_num_tracks(), 1)
        track = data.get_track(0)
        self.assertEqual(track.name, "Solo")
        # 480 ticks at 120 bpm is 500 ms. The following beat is at 60 bpm, so 1000 ms.
        self.assertEqual(
            note_rows(track),
            [
                (60, 100, 0, 0.0, 500.0),
                (62, 70, 0, 500.0, 1500.0),
            ],
        )

    def test_running_status_and_velocity_zero(self):
        data = load(mb.build_running_status(self.path("run.mid")))
        self.assertEqual(
            note_rows(data.get_track(0)),
            [
                (60, 100, 0, 0.0, 500.0),
                (64, 90, 0, 500.0, 750.0),
            ],
        )
        explicit = load(mb.build_velocity_zero(self.path("vel0.mid")))
        self.assertEqual(note_rows(explicit.get_track(0)), [(60, 110, 0, 0.0, 500.0)])
        note_on = next(event for event in explicit.get_track(0).events if isinstance(event, NoteOnEvent))
        self.assertFalse(note_on.is_note_off())

    def test_running_status_single_byte_channel_events(self):
        """Program change and channel pressure use one data byte.

        A second event of the same type may omit the status byte. The parser
        must not steal the following event's status byte as data.
        """
        data = load(mb.build_running_status_program(self.path("prog.mid")))
        programs = [event.program_number for event in data.get_track(0).events
                    if isinstance(event, ProgramChangeEvent)]
        aftertouch = [event.aftertouch_amount for event in data.get_track(0).events
                      if isinstance(event, ChannelAftertouchEvent)]
        self.assertEqual(programs, [5, 6])
        self.assertEqual(aftertouch, [40, 50])

    def test_same_pitch_overlap_keeps_the_held_note(self):
        data = load(mb.build_overlap_same_pitch(self.path("held.mid")))
        self.assertEqual(note_rows(data.get_track(0)), [(60, 100, 0, 0.0, 1000.0)])

    def test_same_tick_retrigger_makes_two_notes(self):
        data = load(mb.build_same_tick_retrigger(self.path("retrig.mid")))
        self.assertEqual(
            note_rows(data.get_track(0)),
            [
                (60, 100, 0, 0.0, 500.0),
                (60, 70, 0, 500.0, 1000.0),
            ],
        )
        self.assertEqual(data.get_track(0).notes[0].release_velocity, None)

    def test_hanging_note_and_orphan_note_off_are_dropped(self):
        data = load(mb.build_hanging_and_orphan(self.path("hang.mid")))
        self.assertEqual(data.get_track(0).notes, [])

    def test_zero_length_note_and_sysex(self):
        data = load(mb.build_zero_length(self.path("zero.mid")))
        rows = note_rows(data.get_track(0))
        self.assertEqual(rows, [(60, 100, 0, 0.0, 0.0)])

    def test_smpte_division_is_frames_per_second(self):
        data = load(mb.build_smpte(self.path("smpte.mid")))
        self.assertFalse(data.is_ticks_per_beat)
        self.assertEqual(data.ticks_per_second, 25 * 40)
        # 1000 ticks at 1000 ticks/second is one second.
        self.assertEqual(note_rows(data.get_track(0)), [(60, 100, 0, 0.0, 1000.0)])

    def test_long_variable_length_delta(self):
        data = load(mb.build_long_delta(self.path("long.mid")))
        start = data.get_track(0).notes[0].start_time
        # 100000 ticks * 500 ms / 480 ticks.
        self.assertAlmostEqual(start, 100000 * 500 / 480, places=3)

    def test_format2_is_rejected(self):
        with self.assertRaises(NotSupportedException) as caught:
            load(mb.build_format2(self.path("fmt2.mid")))
        self.assertIn("format 2", str(caught.exception))

    def test_malformed_files_raise(self):
        garbage = self.path("garbage.mid")
        garbage.write_bytes(b"this is not a midi file")
        with self.assertRaises(Exception):
            load(garbage)
        truncated = self.path("truncated.mid")
        good = mb.build_format0(self.path("good.mid")).read_bytes()
        truncated.write_bytes(good[:20])
        with self.assertRaises((MidiParserException, IndexError, Exception)):
            load(truncated)
        empty = self.path("empty.mid")
        empty.write_bytes(b"")
        with self.assertRaises(Exception):
            load(empty)

    def test_header_track_count_can_disagree_without_hanging(self):
        events = [mb.tempo(0, mb.TEMPO_120), mb.note_on(0, 60, 10), mb.note_off(10, 60, 0), mb.end_of_track()]
        path = mb.write_midi(self.path("count.mid"), 1, mb.PPQ, [events], header_track_count=4)
        data = load(path)
        self.assertEqual(data.num_tracks, 4)
        self.assertEqual(data.get_num_tracks(), 1)
        self.assertEqual(len(data.get_track(0).notes), 1)

    def test_middle_c_note_names(self):
        for middle, expected in (("C3", "C3"), ("C4", "C4"), ("C5", "C5")):
            note = Note(0, 0, 60, 1, 0, middle_c=middle)
            note.set_end_time(0)
            self.assertEqual(str(note).split()[1], expected)

    def test_controller_names(self):
        self.assertEqual(Util.controller_string(1), "Modulation")
        self.assertEqual(Util.controller_string(64), "Damper pedal (sustain)")
        self.assertIsNone(Util.controller_string(3))
        self.assertIn("General Purpose", Util.controller_string(16))


if __name__ == "__main__":
    unittest.main()
