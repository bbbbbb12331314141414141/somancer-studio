"""Tests for plugin SDK and vocal harmony services."""

import os
import json
import pytest
import tempfile

from aimusic.services.plugin_service import (
    PluginService, PluginManifest, VALID_TYPES,
)
from aimusic.services.vocal_harmony_service import (
    VocalHarmonyService, _parse_key, _harmony_at_interval,
)


# ── Plugin Service Tests ───────────────────────────────────────────────────────

class TestPluginService:

    def test_valid_types_set(self):
        """VALID_TYPES contains expected plugin categories."""
        assert "effect" in VALID_TYPES
        assert "generator" in VALID_TYPES
        assert "ai" in VALID_TYPES
        assert "voice_model" in VALID_TYPES

    def test_discover_empty_dir(self, tmp_path):
        """Discovering in an empty directory returns zero plugins."""
        svc = PluginService(plugin_dirs=[str(tmp_path)])
        assert svc.discover() == []

    def test_discover_valid_plugin(self, tmp_path):
        """A valid plugin directory with manifest.json is discovered."""
        plugin_dir = tmp_path / "my-plugin"
        plugin_dir.mkdir()
        manifest = {
            "id": "my-plugin", "name": "My Plugin",
            "version": "1.0.0", "type": "effect",
            "author": "Test", "description": "A test plugin",
            "entry_point": "plugin.py", "api_version": "1.0",
        }
        (plugin_dir / "manifest.json").write_text(json.dumps(manifest))

        svc = PluginService(plugin_dirs=[str(tmp_path)])
        found = svc.discover()
        assert len(found) == 1
        assert found[0].id == "my-plugin"
        assert found[0].plugin_type == "effect"

    def test_discover_invalid_type(self, tmp_path):
        """A manifest with an invalid type is skipped."""
        plugin_dir = tmp_path / "bad-plugin"
        plugin_dir.mkdir()
        manifest = {
            "id": "bad", "name": "Bad", "version": "1.0.0",
            "type": "invalid_type",
        }
        (plugin_dir / "manifest.json").write_text(json.dumps(manifest))

        svc = PluginService(plugin_dirs=[str(tmp_path)])
        found = svc.discover()
        assert len(found) == 0

    def test_discover_missing_manifest(self, tmp_path):
        """A directory without manifest.json is skipped."""
        plugin_dir = tmp_path / "no-manifest"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.py").write_text("# no manifest")

        svc = PluginService(plugin_dirs=[str(tmp_path)])
        assert svc.discover() == []

    def test_create_example_plugin(self, tmp_path):
        """create_example_plugin_dir creates expected files."""
        target = str(tmp_path / "example-gain")
        PluginService.create_example_plugin_dir(target)

        assert os.path.isfile(os.path.join(target, "manifest.json"))
        assert os.path.isfile(os.path.join(target, "plugin.py"))
        assert os.path.isfile(os.path.join(target, "README.md"))

        with open(os.path.join(target, "manifest.json")) as f:
            data = json.load(f)
        assert data["id"] == "example-gain"
        assert data["type"] == "effect"

    def test_load_example_plugin(self, tmp_path):
        """Example plugin loads and provides an EffectPlugin instance."""
        target = str(tmp_path / "example-gain")
        PluginService.create_example_plugin_dir(target)

        svc = PluginService(plugin_dirs=[str(tmp_path)])
        svc.discover_and_register()

        effect = svc.get_loaded_effect("example-gain")
        assert effect is not None
        assert effect.name == "Example Gain"

    def test_example_plugin_process(self, tmp_path):
        """Example gain plugin processes audio correctly."""
        try:
            import numpy as np
        except ImportError:
            pytest.skip("numpy not installed")

        target = str(tmp_path / "example-gain")
        PluginService.create_example_plugin_dir(target)
        svc = PluginService(plugin_dirs=[str(tmp_path)])
        svc.discover_and_register()

        effect = svc.get_loaded_effect("example-gain")
        assert effect is not None

        audio = np.ones((1000, 2), dtype=np.float32) * 0.5
        result = effect.process(audio, 48000, {"gain_db": 6.0})
        assert result.shape == audio.shape
        # +6 dB ≈ ×2, clipped to 1.0
        assert float(result.max()) <= 1.0

    def test_unload_plugin(self, tmp_path):
        """Unloading a plugin frees it."""
        target = str(tmp_path / "example-gain")
        PluginService.create_example_plugin_dir(target)

        svc = PluginService(plugin_dirs=[str(tmp_path)])
        svc.discover_and_register()
        svc.load_plugin("example-gain")

        success = svc.unload_plugin("example-gain")
        assert success is True
        assert svc.get_plugin("example-gain").loaded is False

    def test_get_unknown_plugin(self, tmp_path):
        """get_plugin returns None for unknown plugin IDs."""
        svc = PluginService(plugin_dirs=[str(tmp_path)])
        assert svc.get_plugin("nonexistent") is None


# ── Vocal Harmony Tests ────────────────────────────────────────────────────────

class TestVocalHarmony:

    LEAD = [
        {"pitch": 60, "start": 0.0, "duration": 1.0, "velocity": 80},
        {"pitch": 62, "start": 1.0, "duration": 1.0, "velocity": 80},
        {"pitch": 64, "start": 2.0, "duration": 1.0, "velocity": 80},
        {"pitch": 65, "start": 3.0, "duration": 1.0, "velocity": 80},
    ]

    def test_parse_major_key(self):
        """Major key parses correctly."""
        root, scale = _parse_key("C Major")
        assert root == 0
        assert scale == [0, 2, 4, 5, 7, 9, 11]

    def test_parse_minor_key(self):
        """Minor key parses correctly."""
        root, scale = _parse_key("A Minor")
        assert root == 9
        assert scale == [0, 2, 3, 5, 7, 8, 10]

    def test_parse_bb_major(self):
        """Bb Major parses correctly."""
        root, scale = _parse_key("Bb Major")
        assert root == 10

    def test_generate_duet(self):
        """Duet (voice_count=1) produces lead + 1 harmony voice."""
        svc = VocalHarmonyService()
        result = svc.generate_harmonies(self.LEAD, key="C Major", voice_count=1)
        assert len(result.lead) == 4
        assert len(result.voices) == 1
        assert result.voice_count == 2

    def test_generate_quartet(self):
        """Quartet (voice_count=3) produces lead + 3 harmony voices."""
        svc = VocalHarmonyService()
        result = svc.generate_harmonies(self.LEAD, key="C Major", voice_count=3)
        assert result.voice_count == 4
        assert len(result.voices) == 3

    def test_harmony_notes_in_range(self):
        """All harmony notes fall within voice range bounds."""
        svc = VocalHarmonyService()
        result = svc.generate_harmonies(self.LEAD, key="C Major", voice_count=3)
        for voice_name, notes in result.voices.items():
            lo, hi = VocalHarmonyService.VOICE_RANGES[voice_name]
            for n in notes:
                assert lo <= n.pitch <= hi, \
                    f"Voice {voice_name} note {n.pitch} out of range [{lo},{hi}]"

    def test_harmony_same_timing(self):
        """Harmony notes preserve lead note timing."""
        svc = VocalHarmonyService()
        result = svc.generate_harmonies(self.LEAD, key="C Major", voice_count=1)
        for voice_notes in result.voices.values():
            assert len(voice_notes) == len(self.LEAD)
            for h, l in zip(voice_notes, self.LEAD):
                assert h.start == l["start"]
                assert h.duration == l["duration"]

    def test_parallel_harmony(self):
        """Parallel harmony at P5 generates correct number of notes."""
        svc = VocalHarmonyService()
        notes = svc.generate_parallel_harmony(
            self.LEAD, interval_semitones=7, key="C Major"
        )
        assert len(notes) == len(self.LEAD)
        assert notes[0].voice == "harmony"

    def test_voices_to_midi_tracks(self):
        """voices_to_midi_tracks returns MIDI-compatible dicts."""
        svc = VocalHarmonyService()
        result = svc.generate_harmonies(self.LEAD, key="C Major", voice_count=2)
        tracks = svc.voices_to_midi_tracks(result, include_lead=True)

        assert len(tracks) >= 3  # lead + 2 voices
        for t in tracks:
            assert "name" in t
            assert "notes" in t
            assert "channel" in t
            assert "instrument" in t

    def test_empty_lead(self):
        """Empty lead notes returns empty harmony."""
        svc = VocalHarmonyService()
        result = svc.generate_harmonies([], key="C Major", voice_count=2)
        assert len(result.lead) == 0
        for notes in result.voices.values():
            assert len(notes) == 0
