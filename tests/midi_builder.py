"""Write small Standard MIDI Files for tests.

The builder speaks the MIDI spec (variable-length quantities, running status,
meta events). Tests then check what the add-on's parser actually returns.
"""

from __future__ import annotations

import struct
from pathlib import Path


def vlq(value: int) -> bytes:
    """Encode a non-negative integer as a MIDI variable-length quantity."""
    if value < 0:
        raise ValueError(value)
    chunks = [value & 0x7F]
    value >>= 7
    while value:
        chunks.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(chunks))


def _meta(delta: int, meta_type: int, data: bytes = b"") -> bytes:
    return vlq(delta) + bytes((0xFF, meta_type)) + vlq(len(data)) + data


def tempo(delta: int, microseconds_per_quarter: int) -> bytes:
    return _meta(delta, 0x51, microseconds_per_quarter.to_bytes(3, "big"))


def time_signature(delta: int, numerator: int, denominator_pow2: int, clocks_per_click: int = 24,
                   thirty_seconds: int = 8) -> bytes:
    return _meta(delta, 0x58, bytes((numerator, denominator_pow2, clocks_per_click, thirty_seconds)))


def key_signature(delta: int, sharps_flats: int, minor: int = 0) -> bytes:
    return _meta(delta, 0x59, bytes((sharps_flats & 0xFF, minor)))


def text_meta(delta: int, meta_type: int, text: str) -> bytes:
    return _meta(delta, meta_type, text.encode("utf-8"))


def track_name(delta: int, name: str) -> bytes:
    return text_meta(delta, 0x03, name)


def end_of_track(delta: int = 0) -> bytes:
    return _meta(delta, 0x2F, b"")


def channel(delta: int, status: int, data: bytes) -> bytes:
    return vlq(delta) + bytes((status,)) + data


def note_on(delta: int, note: int, velocity: int, channel_index: int = 0) -> bytes:
    return channel(delta, 0x90 | channel_index, bytes((note, velocity)))


def note_off(delta: int, note: int, velocity: int = 0, channel_index: int = 0) -> bytes:
    return channel(delta, 0x80 | channel_index, bytes((note, velocity)))


def control_change(delta: int, controller: int, value: int, channel_index: int = 0) -> bytes:
    return channel(delta, 0xB0 | channel_index, bytes((controller, value)))


def program_change(delta: int, program: int, channel_index: int = 0) -> bytes:
    return channel(delta, 0xC0 | channel_index, bytes((program,)))


def channel_aftertouch(delta: int, amount: int, channel_index: int = 0) -> bytes:
    return channel(delta, 0xD0 | channel_index, bytes((amount,)))


def pitch_bend(delta: int, bend: int, channel_index: int = 0) -> bytes:
    """``bend`` is the 14-bit wheel value (8192 is center)."""
    return channel(delta, 0xE0 | channel_index, bytes((bend & 0x7F, (bend >> 7) & 0x7F)))


def sysex(delta: int, payload: bytes) -> bytes:
    body = payload if payload.endswith(b"\xF7") else payload + b"\xF7"
    return vlq(delta) + bytes((0xF0,)) + vlq(len(body)) + body


def running(delta: int, data: bytes) -> bytes:
    """Data bytes that omit the status byte (MIDI running status)."""
    return vlq(delta) + data


def track(events: list[bytes]) -> bytes:
    body = b"".join(events)
    return b"MTrk" + struct.pack(">I", len(body)) + body


def header(fmt: int, track_count: int, division: int) -> bytes:
    body = struct.pack(">HHH", fmt, track_count, division & 0xFFFF)
    return b"MThd" + struct.pack(">I", 6) + body


def write_midi(path: str | Path, fmt: int, division: int, tracks: list[list[bytes]],
               header_track_count: int | None = None) -> Path:
    path = Path(path)
    count = len(tracks) if header_track_count is None else header_track_count
    blob = header(fmt, count, division) + b"".join(track(events) for events in tracks)
    path.write_bytes(blob)
    return path


PPQ = 480
# 120 bpm == 500_000 microseconds per quarter note.
TEMPO_120 = 500_000
TEMPO_60 = 1_000_000


def build_piano_format1(path: str | Path) -> Path:
    """Committed-fixture equivalent: format 1, 120 bpm, 480 ppq.

    Piano notes (start ms, end ms), all channel 0:
      C4 (60) velocity 100 from 0 to 500
      E4 (64) velocity 80 from 0 to 500
      G4 (67) velocity 127 from 500 to 750
      C4 (60) velocity 40 from 1000 to 1500
    Bass:
      C2 (36) velocity 90 from 0 to 2000, with CC 7 at 0 ms (100) and 500 ms (20)
    """
    tempo_track = [
        track_name(0, "Tempo"),
        tempo(0, TEMPO_120),
        time_signature(0, 4, 2),
        time_signature(1920, 3, 3),
        key_signature(0, 2, 0),
        text_meta(0, 1, "piano study"),
        end_of_track(0),
    ]
    piano = [
        track_name(0, "Piano"),
        note_on(0, 60, 100),
        note_on(0, 64, 80),
        note_off(480, 60, 64),
        note_off(0, 64, 0),
        note_on(0, 67, 127),
        note_off(240, 67, 0),
        note_on(240, 60, 40),
        note_off(480, 60, 0),
        end_of_track(0),
    ]
    bass = [
        track_name(0, "Bass"),
        note_on(0, 36, 90),
        control_change(0, 7, 100),
        control_change(480, 7, 20),
        pitch_bend(0, 8192 + 256),
        program_change(0, 33),
        note_off(1440, 36, 0),
        end_of_track(0),
    ]
    empty = [track_name(0, "Empty"), end_of_track(0)]
    return write_midi(path, 1, PPQ, [tempo_track, piano, bass, empty])


def build_format0(path: str | Path) -> Path:
    """Single-track file with a tempo change halfway through."""
    events = [
        track_name(0, "Solo"),
        tempo(0, TEMPO_120),
        time_signature(0, 4, 2),
        note_on(0, 60, 100),
        note_off(480, 60, 0),
        tempo(0, TEMPO_60),
        note_on(0, 62, 70),
        note_off(480, 62, 0),
        end_of_track(0),
    ]
    return write_midi(path, 0, PPQ, [events])


def build_running_status(path: str | Path) -> Path:
    """Note-on running status, including note-on with velocity 0 as note-off."""
    events = [
        tempo(0, TEMPO_120),
        note_on(0, 60, 100),
        running(480, bytes((60, 0))),
        running(0, bytes((64, 90))),
        running(240, bytes((64, 0))),
        end_of_track(0),
    ]
    return write_midi(path, 0, PPQ, [events])


def build_running_status_program(path: str | Path) -> Path:
    """Program change followed by another program change that omits the status byte."""
    events = [
        tempo(0, TEMPO_120),
        program_change(0, 5),
        running(16, bytes((6,))),
        channel_aftertouch(0, 40),
        running(8, bytes((50,))),
        end_of_track(0),
    ]
    return write_midi(path, 0, PPQ, [events])


def build_velocity_zero(path: str | Path) -> Path:
    events = [
        tempo(0, TEMPO_120),
        note_on(0, 60, 110),
        note_on(480, 60, 0),
        end_of_track(0),
    ]
    return write_midi(path, 0, PPQ, [events])


def build_overlap_same_pitch(path: str | Path) -> Path:
    """A second note-on while the pitch is still held, with the note-off later.

    The parser keeps the first note and drops the second note-on unless a
    note-off lands on the same tick (see ``build_same_tick_retrigger``).
    """
    events = [
        tempo(0, TEMPO_120),
        note_on(0, 60, 100),
        note_on(480, 60, 50),
        note_off(480, 60, 0),
        note_off(480, 60, 0),
        end_of_track(0),
    ]
    return write_midi(path, 0, PPQ, [events])


def build_same_tick_retrigger(path: str | Path) -> Path:
    """Note-on then note-off on the same tick retriggers the pitch."""
    events = [
        tempo(0, TEMPO_120),
        note_on(0, 60, 100),
        note_on(480, 60, 70),
        note_off(0, 60, 20),
        note_off(480, 60, 0),
        end_of_track(0),
    ]
    return write_midi(path, 0, PPQ, [events])


def build_hanging_and_orphan(path: str | Path) -> Path:
    events = [
        tempo(0, TEMPO_120),
        note_off(0, 60, 0),
        note_on(0, 62, 80),
        end_of_track(0),
    ]
    return write_midi(path, 0, PPQ, [events])


def build_zero_length(path: str | Path) -> Path:
    events = [
        tempo(0, TEMPO_120),
        note_on(0, 60, 100),
        note_off(0, 60, 0),
        sysex(0, bytes((0x7E, 0x00))),
        end_of_track(0),
    ]
    return write_midi(path, 0, PPQ, [events])


def build_smpte(path: str | Path) -> Path:
    """25 fps, 40 ticks per frame. 1000 ticks is one second under the MIDI spec."""
    division = ((0xE7 << 8) | 40)  # SMPTE 25 fps, 40 ticks/frame
    events = [
        note_on(0, 60, 100),
        note_off(1000, 60, 0),
        end_of_track(0),
    ]
    return write_midi(path, 0, division, [events])


def build_format2(path: str | Path) -> Path:
    events = [end_of_track(0)]
    return write_midi(path, 2, PPQ, [events])


def build_long_delta(path: str | Path) -> Path:
    events = [
        tempo(0, TEMPO_120),
        note_on(100000, 60, 100),
        note_off(480, 60, 0),
        end_of_track(0),
    ]
    return write_midi(path, 0, PPQ, [events])


def build_duplicate_track_names(path: str | Path) -> Path:
    first = [track_name(0, "Piano"), note_on(0, 60, 100), note_off(480, 60, 0), end_of_track()]
    second = [track_name(0, "Piano"), note_on(0, 62, 90), note_off(480, 62, 0), end_of_track()]
    tempo_track = [tempo(0, TEMPO_120), end_of_track()]
    return write_midi(path, 1, PPQ, [tempo_track, first, second])


def build_blank_track_name(path: str | Path) -> Path:
    events = [
        tempo(0, TEMPO_120),
        track_name(0, ""),
        note_on(0, 60, 100),
        note_off(480, 60, 0),
        end_of_track(),
    ]
    return write_midi(path, 0, PPQ, [events])


def build_chromatic_scale(path: str | Path, pitches, step_ticks: int = 480, velocity: int = 100,
                          duration_ticks: int = 480) -> Path:
    events = [tempo(0, TEMPO_120), track_name(0, "Scale")]
    first = True
    for pitch in pitches:
        events.append(note_on(0 if first else step_ticks, pitch, velocity))
        events.append(note_off(duration_ticks, pitch, 0))
        first = False
    events.append(end_of_track())
    return write_midi(path, 0, PPQ, [events])


def build_overlap_pair(path: str | Path) -> Path:
    """Two short C4 notes whose MIDI ranges do not overlap, plus a later G4.

    The C notes start 250 ms apart. An NLA action of about 10 frames still
    overlaps at 24 fps, while the parser keeps both notes.
    """
    events = [
        tempo(0, TEMPO_120),
        track_name(0, "Overlap"),
        note_on(0, 60, 100),
        note_off(120, 60, 0),
        note_on(120, 60, 90),
        note_off(480, 60, 0),
        note_on(1200, 67, 80),
        note_off(480, 67, 0),
        end_of_track(0),
    ]
    return write_midi(path, 0, PPQ, [events])


def build_polyphonic_overlap(path: str | Path) -> Path:
    """C4 held for one second, with E4 starting halfway through."""
    events = [
        tempo(0, TEMPO_120),
        track_name(0, "Poly"),
        note_on(0, 60, 100),
        note_on(480, 64, 80),
        note_off(480, 60, 0),
        note_off(0, 64, 0),
        end_of_track(0),
    ]
    return write_midi(path, 0, PPQ, [events])


def build_cc_and_notes(path: str | Path) -> Path:
    events = [
        tempo(0, TEMPO_120),
        track_name(0, "CC"),
        note_on(0, 60, 100),
        control_change(0, 1, 0),
        note_off(480, 60, 0),
        control_change(0, 1, 127),
        note_on(480, 64, 60),
        note_off(480, 64, 0),
        end_of_track(0),
    ]
    return write_midi(path, 0, PPQ, [events])


def build_many_same_pitch(path: str | Path, count: int = 4, velocities=None) -> Path:
    velocities = list(velocities or [100, 40, 10, 127])
    events = [tempo(0, TEMPO_120), track_name(0, "Row")]
    for index in range(count):
        velocity = velocities[index % len(velocities)]
        events.append(note_on(0 if index == 0 else 960, 60, velocity))
        events.append(note_off(480, 60, 0))
    events.append(end_of_track())
    return write_midi(path, 0, PPQ, [events])


def build_lengths(path: str | Path) -> Path:
    """C4 held 480 ticks (500 ms) then C4 held 960 ticks (1000 ms)."""
    events = [
        tempo(0, TEMPO_120),
        track_name(0, "Lengths"),
        note_on(0, 60, 100),
        note_off(480, 60, 0),
        note_on(480, 60, 100),
        note_off(960, 60, 0),
        end_of_track(0),
    ]
    return write_midi(path, 0, PPQ, [events])
