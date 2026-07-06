"""Tests for audio helper utilities."""

import pytest
from aimusic.utils.audio_helpers import (
    beats_to_seconds,
    seconds_to_beats,
    bars_to_seconds,
    midi_pitch_to_name,
    note_name_to_midi,
    quantize_beat,
    target_lufs,
    format_bytes,
)


def test_beats_to_seconds():
    assert beats_to_seconds(4, 120) == pytest.approx(2.0)
    assert beats_to_seconds(1, 60)  == pytest.approx(1.0)
    assert beats_to_seconds(8, 160) == pytest.approx(3.0)


def test_seconds_to_beats():
    assert seconds_to_beats(2.0, 120) == pytest.approx(4.0)
    assert seconds_to_beats(1.0, 60)  == pytest.approx(1.0)


def test_bars_to_seconds():
    assert bars_to_seconds(2, 120) == pytest.approx(4.0)   # 2 bars × 4 beats = 8 beats @ 120bpm
    assert bars_to_seconds(1, 60)  == pytest.approx(4.0)   # 4 beats @ 60bpm = 4s


def test_midi_pitch_to_name():
    assert midi_pitch_to_name(60) == "C4"
    assert midi_pitch_to_name(69) == "A4"
    assert midi_pitch_to_name(21) == "A0"
    assert midi_pitch_to_name(0)  == "C-1"


def test_note_name_to_midi():
    assert note_name_to_midi("C4")  == 60
    assert note_name_to_midi("A4")  == 69
    assert note_name_to_midi("C#4") == 61
    assert note_name_to_midi("Bb3") == 58
    assert note_name_to_midi("A0")  == 21


def test_note_name_to_midi_invalid():
    with pytest.raises(ValueError):
        note_name_to_midi("X4")


def test_quantize_beat():
    assert quantize_beat(0.3,  0.25) == pytest.approx(0.25)
    assert quantize_beat(0.13, 0.25) == pytest.approx(0.0)
    assert quantize_beat(0.9,  0.5)  == pytest.approx(1.0)


def test_target_lufs():
    assert target_lufs("spotify")      == -14.0
    assert target_lufs("apple_music")  == -16.0
    assert target_lufs("broadcast")    == -23.0
    assert target_lufs("unknown")      == -14.0  # default


def test_format_bytes():
    assert format_bytes(512)         == "512.0 B"
    assert format_bytes(1024)        == "1.0 KB"
    assert format_bytes(1024 * 1024) == "1.0 MB"
