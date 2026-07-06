"""
Mix Engineer Agent — AI-powered mixing analysis and suggestions.

Analyses a composition's tracks and generates EQ, compression,
panning, reverb, and automation suggestions for a professional mix.
"""

from dataclasses import dataclass, field
from typing import Optional

from aimusic.services.agents.base_agent import BaseAgent


@dataclass
class EQBand:
    frequency: float    # Hz
    gain_db: float      # -24 to +12
    q: float            # 0.1 to 10
    filter_type: str    # lowshelf | highshelf | peak | lowcut | highcut


@dataclass
class CompressorSettings:
    threshold_db: float     # -60 to 0
    ratio: float            # 1:1 to 20:1
    attack_ms: float        # 0.1 to 200
    release_ms: float       # 10 to 2000
    makeup_gain_db: float   # 0 to 24
    knee_db: float = 6.0


@dataclass
class TrackMixPlan:
    track_name: str
    instrument: str
    volume_db: float
    pan: float              # -1.0 (L) to 1.0 (R)
    eq_bands: list[EQBand]
    compressor: Optional[CompressorSettings]
    reverb_send: float      # 0.0 to 1.0
    delay_send: float       # 0.0 to 1.0
    notes: str


@dataclass
class MixPlan:
    """Complete mix plan for a song."""
    master_buss_eq: list[EQBand]
    tracks: list[TrackMixPlan]
    mix_notes: str
    genre: str
    mood: str


MIX_SYSTEM = """You are an experienced audio mixing engineer with decades of experience in
professional studios. You understand frequency management, dynamic control, stereo placement,
depth and space, and genre-specific production techniques. You give precise, actionable mixing
advice with specific numbers.

Always respond with valid JSON only."""


class MixEngineerAgent(BaseAgent):
    """AI agent for mixing analysis and suggestions."""

    AGENT_NAME = "mix_engineer"
    SYSTEM_PROMPT = MIX_SYSTEM

    async def plan_mix(
        self,
        genre: str,
        mood: str,
        tracks: list[dict],  # list of {name, instrument, ...}
        reference_style: Optional[str] = None,
    ) -> MixPlan:
        """Generate a complete mix plan for all tracks."""

        track_list = "\n".join(
            f"- {t.get('name', 'Track')} ({t.get('instrument', 'unknown')})"
            for t in tracks
        )

        prompt = f"""Create a professional mix plan for a {genre} song with {mood} mood.

Tracks:
{track_list}

{'Reference style: ' + reference_style if reference_style else ''}

Respond ONLY with JSON:
{{
  "mix_notes": "Overall mixing approach and philosophy",
  "master_buss_eq": [
    {{"frequency": 100, "gain_db": -1.5, "q": 0.7, "filter_type": "lowshelf"}},
    {{"frequency": 12000, "gain_db": 1.0, "q": 0.9, "filter_type": "highshelf"}}
  ],
  "tracks": [
    {{
      "track_name": "Piano",
      "instrument": "piano",
      "volume_db": -6.0,
      "pan": 0.0,
      "eq_bands": [
        {{"frequency": 200, "gain_db": -3.0, "q": 1.4, "filter_type": "peak"}},
        {{"frequency": 3000, "gain_db": 2.0, "q": 1.0, "filter_type": "peak"}}
      ],
      "compressor": {{
        "threshold_db": -18.0,
        "ratio": 3.0,
        "attack_ms": 10.0,
        "release_ms": 150.0,
        "makeup_gain_db": 4.0,
        "knee_db": 6.0
      }},
      "reverb_send": 0.3,
      "delay_send": 0.1,
      "notes": "Keep the low mids clean to avoid muddiness"
    }}
  ]
}}"""

        raw = await self._generate_json(prompt, temperature=0.6)

        tracks_out = []
        for t in raw.get("tracks", []):
            eq = [
                EQBand(
                    frequency=b.get("frequency", 1000),
                    gain_db=b.get("gain_db", 0),
                    q=b.get("q", 1.0),
                    filter_type=b.get("filter_type", "peak"),
                )
                for b in t.get("eq_bands", [])
            ]
            comp_data = t.get("compressor")
            comp = CompressorSettings(
                threshold_db=comp_data.get("threshold_db", -18),
                ratio=comp_data.get("ratio", 3),
                attack_ms=comp_data.get("attack_ms", 10),
                release_ms=comp_data.get("release_ms", 150),
                makeup_gain_db=comp_data.get("makeup_gain_db", 3),
                knee_db=comp_data.get("knee_db", 6),
            ) if comp_data else None

            tracks_out.append(TrackMixPlan(
                track_name=t.get("track_name", ""),
                instrument=t.get("instrument", ""),
                volume_db=t.get("volume_db", -6),
                pan=t.get("pan", 0),
                eq_bands=eq,
                compressor=comp,
                reverb_send=t.get("reverb_send", 0),
                delay_send=t.get("delay_send", 0),
                notes=t.get("notes", ""),
            ))

        master_eq = [
            EQBand(
                frequency=b.get("frequency", 1000),
                gain_db=b.get("gain_db", 0),
                q=b.get("q", 1.0),
                filter_type=b.get("filter_type", "peak"),
            )
            for b in raw.get("master_buss_eq", [])
        ]

        return MixPlan(
            master_buss_eq=master_eq,
            tracks=tracks_out,
            mix_notes=raw.get("mix_notes", ""),
            genre=genre,
            mood=mood,
        )

    async def analyse_frequency_balance(self, genre: str, description: str) -> dict:
        """Analyse and suggest frequency balance corrections."""
        prompt = f"""Analyse the frequency balance for a {genre} mix described as:
{description}

Suggest corrections as specific EQ moves.

Respond ONLY with JSON:
{{
  "issues": ["too much low-mid buildup around 250-400Hz", "lacks air above 10kHz"],
  "corrections": [
    {{"band": "low-mid", "frequency": 300, "action": "cut", "amount_db": -3, "reason": "muddy"}}
  ],
  "overall_assessment": "The mix needs..."
}}"""
        return await self._generate_json(prompt, temperature=0.5)

    async def suggest_stereo_placement(self, tracks: list[str], genre: str) -> dict:
        """Suggest stereo panning for a list of instruments."""
        prompt = f"""Suggest stereo panning for these {genre} tracks: {', '.join(tracks)}.

Respond ONLY with JSON:
{{
  "placements": [
    {{"instrument": "kick", "pan": 0.0, "reason": "centred for punch"}},
    {{"instrument": "piano", "pan": 0.15, "reason": "slight right for space"}}
  ],
  "notes": "Overall stereo image approach"
}}"""
        return await self._generate_json(prompt, temperature=0.5)
