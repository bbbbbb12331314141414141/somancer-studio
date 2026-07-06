"""
Plugin Service — plugin discovery, loading, lifecycle management.

Sonmancer Plugin SDK v1.0

Plugin types:
  - effect      : audio DSP (EQ, compressor, reverb, etc.)
  - generator   : instrument / synth
  - ai          : custom AI model
  - exporter    : additional export formats
  - visualizer  : waveform/spectrum visualisation
  - theme       : UI theme
  - voice_model : custom singing voice
  - genre_pack  : additional genre data

A plugin is a directory containing:
  manifest.json   — metadata, version, entry-point
  plugin.py       — Python entry-point (for effect/generator/ai types)
  plugin.js       — JS entry-point (for visualizer/theme types)
  assets/         — icons, presets, soundfonts, model weights
"""

from __future__ import annotations

import importlib.util
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── Plugin types ──────────────────────────────────────────────────────────────

VALID_TYPES = {
    "effect", "generator", "ai", "exporter",
    "visualizer", "theme", "voice_model", "genre_pack",
}


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class PluginManifest:
    """Parsed plugin manifest."""
    id: str
    name: str
    version: str
    plugin_type: str
    author: str
    description: str
    entry_point: Optional[str]          # "plugin.py" | "plugin.js" | None
    api_version: str = "1.0"
    tags: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)  # "filesystem" | "network" | "audio"
    config_schema: dict = field(default_factory=dict)


@dataclass
class LoadedPlugin:
    """A plugin that has been discovered and optionally loaded."""
    manifest: PluginManifest
    directory: str
    loaded: bool = False
    module: Any = None          # Python module if loaded
    error: Optional[str] = None


# ── Plugin SDK base classes (for plugin authors) ──────────────────────────────

class EffectPlugin:
    """
    Base class for audio effect plugins.

    Override `process(audio_data, sample_rate, parameters)` to implement.
    """

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def default_parameters(self) -> dict:
        return {}

    def process(
        self,
        audio_data: "np.ndarray",
        sample_rate: int,
        parameters: Optional[dict] = None,
    ) -> "np.ndarray":
        """
        Process audio data.

        Args:
            audio_data: numpy array shape (frames, channels)
            sample_rate: sample rate in Hz
            parameters: plugin-specific parameters

        Returns:
            Processed audio with same shape.
        """
        raise NotImplementedError


class GeneratorPlugin:
    """
    Base class for instrument generator plugins.

    Override `render(midi_notes, sample_rate, parameters)`.
    """

    @property
    def name(self) -> str:
        raise NotImplementedError

    def render(
        self,
        midi_notes: list[dict],
        sample_rate: int,
        bpm: float,
        parameters: Optional[dict] = None,
    ) -> "np.ndarray":
        """Render MIDI notes to audio."""
        raise NotImplementedError


class AIPlugin:
    """
    Base class for AI model plugins.

    Override `generate(prompt, context)`.
    """

    @property
    def name(self) -> str:
        raise NotImplementedError

    def generate(self, prompt: str, context: Optional[dict] = None) -> str:
        """Generate content from prompt."""
        raise NotImplementedError


# ── Plugin Service ────────────────────────────────────────────────────────────

class PluginService:
    """Manages plugin discovery, validation, and loading."""

    def __init__(self, plugin_dirs: Optional[list[str]] = None) -> None:
        default_dirs = [
            os.path.join(os.getcwd(), "plugins"),
            os.path.expanduser("~/.sonmancer/plugins"),
        ]
        self.plugin_dirs = plugin_dirs or default_dirs
        self._plugins: dict[str, LoadedPlugin] = {}

    # ── Discovery ─────────────────────────────────────────────────────────────

    def discover(self) -> list[PluginManifest]:
        """Scan all plugin directories and return discovered manifests."""
        found: list[PluginManifest] = []

        for plugin_dir in self.plugin_dirs:
            if not os.path.isdir(plugin_dir):
                continue
            for entry in os.scandir(plugin_dir):
                if not entry.is_dir():
                    continue
                manifest_path = os.path.join(entry.path, "manifest.json")
                if not os.path.isfile(manifest_path):
                    continue
                try:
                    manifest = self._parse_manifest(manifest_path)
                    found.append(manifest)
                    logger.info(f"Discovered plugin: {manifest.id} v{manifest.version}")
                except (json.JSONDecodeError, KeyError, ValueError) as exc:
                    logger.warning(f"Invalid manifest at {manifest_path}: {exc}")

        return found

    def discover_and_register(self) -> int:
        """Discover all plugins and register them. Returns count."""
        manifests = self.discover()
        for plugin_dir in self.plugin_dirs:
            if not os.path.isdir(plugin_dir):
                continue
            for entry in os.scandir(plugin_dir):
                if not entry.is_dir():
                    continue
                manifest_path = os.path.join(entry.path, "manifest.json")
                if not os.path.isfile(manifest_path):
                    continue
                try:
                    manifest = self._parse_manifest(manifest_path)
                    self._plugins[manifest.id] = LoadedPlugin(
                        manifest=manifest,
                        directory=entry.path,
                    )
                except Exception:
                    pass
        return len(self._plugins)

    # ── Loading ────────────────────────────────────────────────────────────────

    def load_plugin(self, plugin_id: str) -> LoadedPlugin:
        """Load and initialise a registered plugin."""
        if plugin_id not in self._plugins:
            raise KeyError(f"Plugin '{plugin_id}' not registered. Call discover_and_register() first.")

        plugin = self._plugins[plugin_id]
        if plugin.loaded:
            return plugin

        entry = plugin.manifest.entry_point
        if not entry or not entry.endswith(".py"):
            # JS / non-Python plugins are loaded by the frontend
            plugin.loaded = True
            return plugin

        entry_path = os.path.join(plugin.directory, entry)
        if not os.path.isfile(entry_path):
            plugin.error = f"Entry point not found: {entry_path}"
            return plugin

        try:
            spec = importlib.util.spec_from_file_location(
                f"sonmancer_plugin_{plugin_id}", entry_path
            )
            module = importlib.util.module_from_spec(spec)   # type: ignore[arg-type]
            spec.loader.exec_module(module)                    # type: ignore[union-attr]
            plugin.module = module
            plugin.loaded = True
            logger.info(f"Loaded plugin: {plugin_id}")
        except Exception as exc:
            plugin.error = str(exc)
            logger.error(f"Failed to load plugin {plugin_id}: {exc}")

        return plugin

    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin and remove its module from sys.modules."""
        if plugin_id not in self._plugins:
            return False
        plugin = self._plugins[plugin_id]
        module_name = f"sonmancer_plugin_{plugin_id}"
        sys.modules.pop(module_name, None)
        plugin.loaded = False
        plugin.module = None
        return True

    # ── Queries ────────────────────────────────────────────────────────────────

    def list_plugins(self, plugin_type: Optional[str] = None) -> list[LoadedPlugin]:
        """Return all registered plugins, optionally filtered by type."""
        plugins = list(self._plugins.values())
        if plugin_type:
            plugins = [p for p in plugins if p.manifest.plugin_type == plugin_type]
        return plugins

    def get_plugin(self, plugin_id: str) -> Optional[LoadedPlugin]:
        """Return a specific plugin by ID."""
        return self._plugins.get(plugin_id)

    def get_loaded_effect(self, plugin_id: str) -> Optional[EffectPlugin]:
        """Return an EffectPlugin instance if loaded and correct type."""
        plugin = self.load_plugin(plugin_id)
        if not plugin.loaded or plugin.module is None:
            return None
        if hasattr(plugin.module, "Plugin"):
            instance = plugin.module.Plugin()
            if isinstance(instance, EffectPlugin):
                return instance
        return None

    # ── Private ────────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_manifest(path: str) -> PluginManifest:
        """Parse and validate a plugin manifest.json."""
        with open(path) as f:
            data = json.load(f)

        plugin_type = data.get("type", data.get("plugin_type", ""))
        if plugin_type not in VALID_TYPES:
            raise ValueError(
                f"Invalid plugin type: {plugin_type!r}. Must be one of: {VALID_TYPES}"
            )

        return PluginManifest(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            plugin_type=plugin_type,
            author=data.get("author", "Unknown"),
            description=data.get("description", ""),
            entry_point=data.get("entry_point"),
            api_version=data.get("api_version", "1.0"),
            tags=data.get("tags", []),
            permissions=data.get("permissions", []),
            config_schema=data.get("config_schema", {}),
        )

    # ── Example plugin factory (for testing / SDK docs) ───────────────────────

    @staticmethod
    def create_example_plugin_dir(target_dir: str) -> str:
        """
        Write an example effect plugin to `target_dir`.
        Useful for testing the SDK and as a developer template.
        """
        os.makedirs(target_dir, exist_ok=True)

        manifest = {
            "id": "example-gain",
            "name": "Example Gain Plugin",
            "version": "1.0.0",
            "type": "effect",
            "author": "Sonmancer Team",
            "description": "A simple gain/attenuation effect plugin example.",
            "entry_point": "plugin.py",
            "api_version": "1.0",
            "tags": ["gain", "utility"],
            "permissions": ["audio"],
            "config_schema": {
                "gain_db": {
                    "type": "float", "default": 0.0,
                    "min": -24.0, "max": 12.0, "label": "Gain (dB)"
                }
            },
        }

        plugin_code = '''"""Example gain effect plugin for Sonmancer Studio."""

import numpy as np
from aimusic.services.plugin_service import EffectPlugin


class Plugin(EffectPlugin):
    """Simple gain/attenuation effect."""

    @property
    def name(self) -> str:
        return "Example Gain"

    @property
    def default_parameters(self) -> dict:
        return {"gain_db": 0.0}

    def process(self, audio_data, sample_rate, parameters=None):
        params = parameters or self.default_parameters
        gain_db = float(params.get("gain_db", 0.0))
        gain_linear = 10 ** (gain_db / 20.0)
        return np.clip(audio_data * gain_linear, -1.0, 1.0)
'''

        readme = """# Example Gain Plugin

A minimal Sonmancer effect plugin demonstrating the Plugin SDK.

## Files
- `manifest.json` — plugin metadata
- `plugin.py`     — effect implementation

## Usage
Place this directory inside your Sonmancer `plugins/` folder.
"""

        with open(os.path.join(target_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)
        with open(os.path.join(target_dir, "plugin.py"), "w") as f:
            f.write(plugin_code)
        with open(os.path.join(target_dir, "README.md"), "w") as f:
            f.write(readme)

        return target_dir
