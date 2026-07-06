"""
Mastering Engineer Agent — AI-powered mastering chain and loudness targeting.

Generates a complete mastering chain (EQ, compression, limiting, dithering)
targeting specific streaming platform loudness standards.
"""

from dataclasses import dataclass, field
from typing import Optional

from aimusic.services.agents.base_agent import BaseAgent
from aimusic.utils.audio_helpers import PLATFORM_TARGETS


@dataclass
class MasteringBand:
    """A single processing band in the mastering chain."""
    stage: str          # eq | multiband_comp | limiter | exciter | stereo_widener
    enabled: bool
    parameters: dict


@dataclass
class MasteringChain:
    """Complete mastering chain for a song."""
    target_platform: str
    target_lufs: float
    target_peak_db: float
    stages: list[MasteringBand]
    notes: str
    expected_character: str


MASTERING_SYSTEM = """You are a world-class mastering engineer who has mastered thousands of
commercial releases. You understand loudness standards, dynamic range, tonal balance,
stereo imaging, and how music translates across different playback systems.

You give precise, professional mastering chains with specific parameter values.
Always respond with valid JSON only."""


class MasteringEngineerAgent(BaseAgent):
    """AI agent for mastering chain generation."""

    AGENT_NAME = "mastering_engineer"
    SYSTEM_PROMPT = MASTERING_SYSTEM

    async def create_mastering_chain(
        self,
        genre: str,
        mood: str,
        platform: str = "spotify",
        dynamic_range: str = "medium",  # compressed | medium | dynamic
        notes: Optional[str] = None,
    ) -> MasteringChain:
        """Generate a full mastering chain targeting a platform."""

        target_lufs = PLATFORM_TARGETS.get(platform.lower(), -14.0)
        target_peak = -1.0  # True peak

        prompt = f"""Create a professional mastering chain for a {genre} ({mood}) track.

Target platform: {platform} ({target_lufs} LUFS integrated)
True peak ceiling: {target_peak} dBTP
Dynamic range preference: {dynamic_range}
{f"Additional notes: {notes}" if notes else ""}

Respond ONLY with JSON:
{{
  "notes": "Overall mastering philosophy for this track",
  "expected_character": "How the mastered track will sound",
  "stages": [
    {{
      "stage": "eq",
      "enabled": true,
      "parameters": {{
        "type": "linear_phase",
        "bands": [
          {{"frequency": 40, "gain_db": -2.0, "q": 0.7, "type": "highpass"}},
          {{"frequency": 200, "gain_db": -1.0, "q": 1.2, "type": "peak"}},
          {{"frequency": 3500, "gain_db": 0.5, "q": 1.5, "type": "peak"}},
          {{"frequency": 10000, "gain_db": 1.5, "q": 0.8, "type": "highshelf"}}
        ]
      }}
    }},
    {{
      "stage": "multiband_comp",
      "enabled": true,
      "parameters": {{
        "bands": [
          {{"name": "low", "freq_range": [20, 200], "threshold_db": -24, "ratio": 2.5,
            "attack_ms": 30, "release_ms": 200}},
          {{"name": "low_mid", "freq_range": [200, 2000], "threshold_db": -22, "ratio": 2.0,
            "attack_ms": 20, "release_ms": 150}},
          {{"name": "high_mid", "freq_range": [2000, 8000], "threshold_db": -20, "ratio": 1.8,
            "attack_ms": 10, "release_ms": 100}},
          {{"name": "high", "freq_range": [8000, 20000], "threshold_db": -18, "ratio": 1.5,
            "attack_ms": 5, "release_ms": 80}}
        ]
      }}
    }},
    {{
      "stage": "stereo_widener",
      "enabled": true,
      "parameters": {{"width": 1.15, "mono_low_freq": 120}}
    }},
    {{
      "stage": "limiter",
      "enabled": true,
      "parameters": {{
        "ceiling_db": {target_peak},
        "lookahead_ms": 3.0,
        "release_ms": 150,
        "target_lufs": {target_lufs}
      }}
    }}
  ]
}}"""

        raw = await self._generate_json(prompt, temperature=0.5)

        stages = [
            MasteringBand(
                stage=s.get("stage", "eq"),
                enabled=s.get("enabled", True),
                parameters=s.get("parameters", {}),
            )
            for s in raw.get("stages", [])
        ]

        return MasteringChain(
            target_platform=platform,
            target_lufs=target_lufs,
            target_peak_db=target_peak,
            stages=stages,
            notes=raw.get("notes", ""),
            expected_character=raw.get("expected_character", ""),
        )

    async def compare_platform_targets(self) -> dict:
        """Return all platform loudness targets with explanations."""
        prompt = """Explain the loudness normalisation standards for major streaming platforms.
Include practical implications for mastering.

Respond ONLY with JSON:
{
  "platforms": [
    {
      "name": "Spotify",
      "target_lufs": -14.0,
      "true_peak_db": -1.0,
      "notes": "Uses replay gain normalisation; loud masters get turned down"
    }
  ],
  "recommendations": "General best practice advice"
}"""
        return await self._generate_json(prompt, temperature=0.4)

    async def review_master(
        self,
        genre: str,
        measured_lufs: float,
        measured_peak_db: float,
        platform: str,
    ) -> dict:
        """Review a completed master and suggest revisions."""
        target = PLATFORM_TARGETS.get(platform.lower(), -14.0)
        delta = measured_lufs - target

        prompt = f"""Review this mastered {genre} track:
Measured integrated LUFS: {measured_lufs:.1f}
Target for {platform}: {target:.1f} LUFS
Delta: {delta:+.1f} LUFS
True peak: {measured_peak_db:.1f} dBTP

Respond ONLY with JSON:
{{
  "status": "approved|needs_revision",
  "issues": [],
  "corrections": [],
  "overall": "Brief assessment"
}}"""
        return await self._generate_json(prompt, temperature=0.4)
