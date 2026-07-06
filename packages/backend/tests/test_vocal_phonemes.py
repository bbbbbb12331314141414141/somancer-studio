"""Tests for vocal synthesis helpers (no audio I/O needed)."""

import pytest
from aimusic.services.vocal_synthesis_service import (
    text_to_phonemes,
    align_phonemes_to_notes,
    VocalSynthesisService,
    VocalLine,
)


def test_text_to_phonemes_known_words():
    """Known words are mapped to IPA phonemes."""
    phonemes = text_to_phonemes("I love you")
    assert len(phonemes) > 0
    # "I" → "aɪ", "love" → "lʌv", "you" → "juː"
    assert any(ph in ("a", "ɪ", "l", "ʌ", "v", "j", "u") for ph in phonemes)


def test_text_to_phonemes_unknown_words():
    """Unknown words fall back to character-level phonemes."""
    phonemes = text_to_phonemes("glorp flibbet")
    assert len(phonemes) > 0
    assert all(isinstance(p, str) for p in phonemes)


def test_text_to_phonemes_empty():
    """Empty string returns empty list."""
    assert text_to_phonemes("") == []


def test_align_phonemes_to_notes():
    """Phonemes align to note timing."""
    notes = [
        {"pitch": 60, "start": 0.0, "duration": 1.0},
        {"pitch": 62, "start": 1.0, "duration": 1.0},
        {"pitch": 64, "start": 2.0, "duration": 1.0},
    ]
    line = align_phonemes_to_notes("I love you", notes, section="verse")
    assert line.text == "I love you"
    assert line.section == "verse"
    assert len(line.phoneme_segments) > 0


def test_align_phonemes_empty_notes():
    """Empty notes returns VocalLine with no segments."""
    line = align_phonemes_to_notes("Hello world", [], section="chorus")
    assert line.text == "Hello world"
    assert line.phoneme_segments == []


def test_vocal_service_available_engines():
    """get_available_engines returns at least tts_stub and diffsinger."""
    svc = VocalSynthesisService()
    engines = svc.get_available_engines()
    names = [e["name"] for e in engines]
    assert "tts_stub" in names
    assert "diffsinger" in names
    assert all("available" in e for e in engines)


def test_vocal_service_diffsinger_not_implemented():
    """DiffSinger raises NotImplementedError (Phase 6 placeholder)."""
    svc = VocalSynthesisService(engine="diffsinger")
    lines = [VocalLine(text="Hello world", section="verse")]
    with pytest.raises(NotImplementedError):
        svc.synthesise(lines)


def test_vocal_service_unknown_engine():
    """Unknown engine raises ValueError."""
    svc = VocalSynthesisService(engine="unknown_engine")
    lines = [VocalLine(text="Test", section="verse")]
    with pytest.raises(ValueError):
        svc.synthesise(lines)
