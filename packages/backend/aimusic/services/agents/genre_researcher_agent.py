"""
Genre Researcher Agent — research and extract musical characteristics
from public knowledge about a genre.

This agent stores structural/descriptive data only (tempo ranges,
instrumentation, harmonic tendencies, production techniques) and does
NOT store or reproduce copyrighted songs or lyrics.
"""

from dataclasses import dataclass, field
from typing import Optional

from aimusic.services.agents.base_agent import BaseAgent


@dataclass
class GenreProfile:
    """Researched musical profile for a genre."""
    name: str
    description: str
    bpm_min: int
    bpm_max: int
    common_keys: list[str]
    common_instruments: list[str]
    production_techniques: list[str]
    chord_progressions: list[str]
    vocal_style: str
    rhythmic_characteristics: str
    historical_context: str
    subgenres: list[str]
    influences: list[str]
    sources: list[str] = field(default_factory=list)


RESEARCHER_SYSTEM = """You are a musicologist and music production expert with encyclopaedic knowledge
of genres, subgenres, and their musical characteristics. You provide factual, structured information
about music theory, production techniques, instrumentation, and stylistic elements.

You describe the musical characteristics of genres — you never reproduce copyrighted song lyrics,
song titles, or specific commercial recordings. You focus entirely on structural and stylistic data.

Always respond with valid JSON only."""


class GenreResearcherAgent(BaseAgent):
    """AI agent that researches musical genre characteristics."""

    AGENT_NAME = "genre_researcher"
    SYSTEM_PROMPT = RESEARCHER_SYSTEM

    async def research_genre(self, genre_name: str) -> GenreProfile:
        """Research a genre and return its musical profile."""
        prompt = f"""Research the musical characteristics of "{genre_name}" as a music genre.

Provide factual information about its structure, production, and style.
Do NOT include copyrighted song titles or lyrics.

Respond ONLY with JSON:
{{
  "name": "{genre_name}",
  "description": "One to two sentence overview of the genre",
  "bpm_min": 80,
  "bpm_max": 140,
  "common_keys": ["C Minor", "G Minor"],
  "common_instruments": ["Electric Guitar", "Bass", "Drums"],
  "production_techniques": ["Reverb heavy", "Distorted guitars"],
  "chord_progressions": ["i-VI-III-VII", "i-iv-v"],
  "vocal_style": "Description of typical vocal approach",
  "rhythmic_characteristics": "Description of rhythmic feel and patterns",
  "historical_context": "Brief origin and development of the genre",
  "subgenres": ["Subgenre A", "Subgenre B"],
  "influences": ["Parent Genre A", "Style B"],
  "sources": ["General music knowledge"]
}}"""

        raw = await self._generate_json(prompt, temperature=0.5)

        return GenreProfile(
            name=raw.get("name", genre_name),
            description=raw.get("description", ""),
            bpm_min=int(raw.get("bpm_min", 80)),
            bpm_max=int(raw.get("bpm_max", 140)),
            common_keys=raw.get("common_keys", []),
            common_instruments=raw.get("common_instruments", []),
            production_techniques=raw.get("production_techniques", []),
            chord_progressions=raw.get("chord_progressions", []),
            vocal_style=raw.get("vocal_style", ""),
            rhythmic_characteristics=raw.get("rhythmic_characteristics", ""),
            historical_context=raw.get("historical_context", ""),
            subgenres=raw.get("subgenres", []),
            influences=raw.get("influences", []),
            sources=raw.get("sources", ["AI knowledge base"]),
        )

    async def suggest_related_genres(self, genre_name: str) -> list[str]:
        """Return a list of related or adjacent genres."""
        prompt = f"""List 6–10 genres that are musically related to "{genre_name}".
Include parent genres, sibling subgenres, and cross-genre influences.

Respond ONLY with JSON: {{"related": ["Genre A", "Genre B", "Genre C"]}}"""

        raw = await self._generate_json(prompt, temperature=0.6)
        return raw.get("related", [])

    async def compare_genres(self, genre_a: str, genre_b: str) -> dict:
        """Compare two genres across key musical dimensions."""
        prompt = f"""Compare "{genre_a}" and "{genre_b}" musically.

Respond ONLY with JSON:
{{
  "similarities": ["Both use..."],
  "differences": {{
    "tempo": "Genre A is faster/slower...",
    "instrumentation": "...",
    "production": "...",
    "harmony": "..."
  }},
  "fusion_potential": "High/Medium/Low — brief explanation"
}}"""

        return await self._generate_json(prompt, temperature=0.6)
