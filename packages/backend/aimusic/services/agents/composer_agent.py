"""
Composer Agent — AI-powered MIDI composition.

Generates melodies, chord progressions, bass lines, and drum patterns
based on genre, mood, key, and tempo, outputting structured MIDI data.
"""

from dataclasses import dataclass, field
from typing import Optional

from aimusic.services.agents.base_agent import BaseAgent, AgentError


@dataclass
class Note:
    """A single MIDI note event."""
    pitch: int        # MIDI note number (0–127, middle C = 60)
    start: float      # Start time in beats
    duration: float   # Duration in beats
    velocity: int     # MIDI velocity (0–127)


@dataclass
class MidiTrack:
    """A single MIDI track (instrument part)."""
    name: str
    channel: int
    instrument: int   # General MIDI program number (0–127)
    notes: list[Note] = field(default_factory=list)


@dataclass
class CompositionResult:
    """Full composition output."""
    tempo: int
    time_signature_numerator: int
    time_signature_denominator: int
    key: str
    tracks: list[MidiTrack] = field(default_factory=list)
    chord_progression: list[str] = field(default_factory=list)
    structure: list[str] = field(default_factory=list)


@dataclass
class CompositionInput:
    """Parameters for AI composition."""
    genre: str = "pop"
    mood: str = "happy"
    key: str = "C Major"
    bpm: int = 120
    bars: int = 8
    instruments: list[str] = field(default_factory=lambda: ["piano", "bass", "drums"])
    complexity: str = "medium"   # simple | medium | complex
    style_notes: Optional[str] = None


COMPOSER_SYSTEM = """You are an expert music composer and arranger with deep knowledge of music theory,
MIDI composition, harmony, and genre-specific production. You understand chord progressions,
voice leading, rhythmic patterns, and instrumentation across all genres.

You always respond with valid JSON only — no preamble, no explanation, no markdown fences."""


# General MIDI instrument map (common ones)
GM_INSTRUMENTS = {
    "piano":        0,
    "electric_piano": 4,
    "harpsichord":  6,
    "guitar":       25,
    "acoustic_guitar": 24,
    "electric_guitar": 27,
    "bass":         32,
    "electric_bass": 33,
    "strings":      48,
    "synth_strings": 50,
    "choir":        52,
    "trumpet":      56,
    "saxophone":    66,
    "flute":        73,
    "synth_lead":   80,
    "synth_pad":    88,
    "drums":        0,  # channel 10 always
}


class ComposerAgent(BaseAgent):
    """AI agent specialising in MIDI composition."""

    AGENT_NAME = "composer"
    SYSTEM_PROMPT = COMPOSER_SYSTEM

    async def compose(self, params: CompositionInput) -> CompositionResult:
        """
        Generate a complete MIDI composition.

        Returns a CompositionResult with all tracks and metadata.
        """
        # Step 1: Generate musical plan (chords, structure)
        plan = await self._plan_composition(params)

        # Step 2: Generate individual tracks based on plan
        tracks: list[MidiTrack] = []

        for instrument in params.instruments:
            if instrument == "drums":
                track = await self._generate_drum_track(params, plan)
            elif instrument in ("bass", "electric_bass"):
                track = await self._generate_bass_track(params, plan)
            else:
                track = await self._generate_melody_track(instrument, params, plan)
            tracks.append(track)

        return CompositionResult(
            tempo=params.bpm,
            time_signature_numerator=4,
            time_signature_denominator=4,
            key=params.key,
            tracks=tracks,
            chord_progression=plan.get("chord_progression", []),
            structure=plan.get("structure", []),
        )

    async def generate_chord_progression(
        self,
        key: str,
        genre: str,
        mood: str,
        bars: int = 4,
    ) -> list[str]:
        """Generate a chord progression for given context."""
        prompt = f"""Generate a {bars}-bar chord progression for a {genre} song.
Key: {key}
Mood: {mood}
Complexity: medium

Respond ONLY with JSON:
{{"progression": ["Cm", "Ab", "Eb", "Bb"], "bars_per_chord": [2, 2, 2, 2]}}"""

        raw = await self._generate_json(prompt, temperature=0.7)
        return raw.get("progression", ["I", "IV", "V", "I"])

    async def suggest_arrangement(
        self,
        genre: str,
        mood: str,
        duration_bars: int = 32,
    ) -> list[dict]:
        """Suggest a song arrangement (intro, verse, chorus, etc.)."""
        prompt = f"""Plan a {duration_bars}-bar {genre} song arrangement.
Mood: {mood}

Respond ONLY with JSON array of sections:
[
  {{"section": "intro", "bars": 4}},
  {{"section": "verse", "bars": 8}},
  {{"section": "chorus", "bars": 8}},
  {{"section": "verse", "bars": 8}},
  {{"section": "chorus", "bars": 8}},
  {{"section": "outro", "bars": 4}}
]"""

        raw = await self._generate_json(prompt, temperature=0.6)
        return raw if isinstance(raw, list) else raw.get("sections", [])

    # ── Private helpers ───────────────────────────────────────────────────────

    async def _plan_composition(self, params: CompositionInput) -> dict:
        """Generate the musical plan: chords, structure, style notes."""
        prompt = f"""Plan a {params.bars}-bar {params.genre} composition.
Key: {params.key}
Tempo: {params.bpm} BPM
Mood: {params.mood}
Complexity: {params.complexity}

Respond ONLY with JSON:
{{
  "chord_progression": ["Chord1", "Chord2", "Chord3", "Chord4"],
  "bars_per_chord": [2, 2, 2, 2],
  "structure": ["intro", "verse", "chorus"],
  "rhythmic_feel": "straight|swing|syncopated",
  "style_notes": "brief description of production approach"
}}"""

        return await self._generate_json(prompt, temperature=0.65)

    async def _generate_melody_track(
        self, instrument: str, params: CompositionInput, plan: dict
    ) -> MidiTrack:
        """Generate a melody/harmony track as MIDI note data."""
        chords = plan.get("chord_progression", ["C", "F", "G", "C"])
        prompt = f"""Generate MIDI notes for a {instrument} melody.
Genre: {params.genre}
Key: {params.key}
BPM: {params.bpm}
Bars: {params.bars}
Chord progression: {chords}
Mood: {params.mood}

Rules:
- Use MIDI note numbers (middle C = 60)
- start = beat position (0.0 = bar 1 beat 1)
- duration = length in beats (1.0 = quarter note)
- velocity = 0–127

Respond ONLY with JSON:
{{
  "notes": [
    {{"pitch": 60, "start": 0.0, "duration": 1.0, "velocity": 80}},
    {{"pitch": 62, "start": 1.0, "duration": 0.5, "velocity": 75}}
  ]
}}"""

        raw = await self._generate_json(prompt, temperature=0.75)
        notes_data = raw.get("notes", [])

        notes = [
            Note(
                pitch=n.get("pitch", 60),
                start=n.get("start", 0.0),
                duration=n.get("duration", 1.0),
                velocity=min(127, max(1, n.get("velocity", 80))),
            )
            for n in notes_data
            if isinstance(n, dict)
        ]

        program = GM_INSTRUMENTS.get(instrument.lower(), 0)
        return MidiTrack(
            name=instrument.capitalize(),
            channel=1,
            instrument=program,
            notes=notes,
        )

    async def _generate_bass_track(self, params: CompositionInput, plan: dict) -> MidiTrack:
        """Generate a bass line following the chord progression."""
        chords = plan.get("chord_progression", ["C", "F", "G", "C"])
        prompt = f"""Generate a {params.genre} bass line.
Key: {params.key}
BPM: {params.bpm}
Bars: {params.bars}
Chords: {chords}
Mood: {params.mood}

Bass notes are typically in octave 2–3 (MIDI 28–52).
Respond ONLY with JSON: {{"notes": [{{"pitch": 36, "start": 0.0, "duration": 1.0, "velocity": 90}}]}}"""

        raw = await self._generate_json(prompt, temperature=0.65)
        notes = [
            Note(
                pitch=max(24, min(60, n.get("pitch", 36))),
                start=n.get("start", 0.0),
                duration=n.get("duration", 1.0),
                velocity=min(127, max(1, n.get("velocity", 90))),
            )
            for n in raw.get("notes", [])
            if isinstance(n, dict)
        ]

        return MidiTrack(
            name="Bass",
            channel=2,
            instrument=GM_INSTRUMENTS["electric_bass"],
            notes=notes,
        )

    async def _generate_drum_track(self, params: CompositionInput, plan: dict) -> MidiTrack:
        """Generate a drum pattern on channel 10 (GM percussion)."""
        prompt = f"""Generate a {params.genre} drum pattern.
BPM: {params.bpm}
Bars: {params.bars}
Feel: {plan.get('rhythmic_feel', 'straight')}

GM drum note numbers:
- Kick drum: 36
- Snare: 38
- Hi-hat closed: 42
- Hi-hat open: 46
- Crash cymbal: 49
- Ride cymbal: 51
- Tom low: 45, Tom mid: 47, Tom high: 50

Respond ONLY with JSON: {{"notes": [{{"pitch": 36, "start": 0.0, "duration": 0.25, "velocity": 100}}]}}"""

        raw = await self._generate_json(prompt, temperature=0.7)
        notes = [
            Note(
                pitch=n.get("pitch", 36),
                start=n.get("start", 0.0),
                duration=n.get("duration", 0.25),
                velocity=min(127, max(1, n.get("velocity", 100))),
            )
            for n in raw.get("notes", [])
            if isinstance(n, dict)
        ]

        return MidiTrack(
            name="Drums",
            channel=10,   # GM percussion channel
            instrument=0,
            notes=notes,
        )
