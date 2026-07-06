"""
Producer Agent — overall creative direction and planning.

The Producer coordinates between Songwriter, Composer, and other
agents to create a coherent musical vision for a song or album.
"""

from dataclasses import dataclass
from typing import Optional

from aimusic.services.agents.base_agent import BaseAgent


@dataclass
class SongBrief:
    """Creative brief for a song."""
    title: str
    genre: str
    mood: str
    theme: str
    target_audience: str
    bpm: int
    key: str
    duration_seconds: int
    structure: list[str]
    instruments: list[str]
    production_notes: str
    lyric_style: str


PRODUCER_SYSTEM = """You are an experienced music producer with decades of experience across
all genres. You understand how to craft commercially and artistically successful songs. You think
holistically about mood, arrangement, production, and storytelling. You give clear, actionable
creative direction.

Always respond with valid JSON only."""


class ProducerAgent(BaseAgent):
    """AI agent providing overall creative direction."""

    AGENT_NAME = "producer"
    SYSTEM_PROMPT = PRODUCER_SYSTEM

    async def create_song_brief(
        self,
        genre: str,
        mood: Optional[str] = None,
        theme: Optional[str] = None,
        target_audience: Optional[str] = None,
        duration_seconds: int = 210,
    ) -> SongBrief:
        """Generate a full creative brief for a new song."""
        prompt = f"""Create a detailed song production brief.

Genre: {genre}
Mood: {mood or 'evocative and memorable'}
Theme: {theme or 'open — suggest something compelling'}
Target audience: {target_audience or 'general listeners'}
Target duration: {duration_seconds} seconds

Respond ONLY with JSON:
{{
  "title": "Suggested Song Title",
  "genre": "{genre}",
  "mood": "...",
  "theme": "...",
  "target_audience": "...",
  "bpm": 120,
  "key": "C Minor",
  "duration_seconds": {duration_seconds},
  "structure": ["intro", "verse", "pre-chorus", "chorus", "verse", "chorus", "bridge", "chorus", "outro"],
  "instruments": ["piano", "bass", "drums", "synth_pad"],
  "production_notes": "Brief description of production approach and signature sounds",
  "lyric_style": "poetic|conversational|storytelling|abstract"
}}"""

        raw = await self._generate_json(prompt, temperature=0.85)

        return SongBrief(
            title=raw.get("title", "Untitled"),
            genre=raw.get("genre", genre),
            mood=raw.get("mood", mood or ""),
            theme=raw.get("theme", theme or ""),
            target_audience=raw.get("target_audience", target_audience or ""),
            bpm=int(raw.get("bpm", 120)),
            key=raw.get("key", "C Major"),
            duration_seconds=int(raw.get("duration_seconds", duration_seconds)),
            structure=raw.get("structure", ["verse", "chorus", "verse", "chorus", "outro"]),
            instruments=raw.get("instruments", ["piano", "bass", "drums"]),
            production_notes=raw.get("production_notes", ""),
            lyric_style=raw.get("lyric_style", "poetic"),
        )

    async def review_lyrics(
        self,
        lyrics: str,
        genre: str,
        mood: str,
    ) -> dict:
        """Provide feedback and suggestions on existing lyrics."""
        prompt = f"""Review these {genre} lyrics (mood: {mood}) and provide constructive feedback.

Lyrics:
{lyrics}

Respond ONLY with JSON:
{{
  "overall_score": 7,
  "strengths": ["strong imagery", "consistent mood"],
  "improvements": ["chorus could be more memorable"],
  "suggested_edits": [{{"original": "line here", "suggested": "better line here"}}],
  "production_notes": "Brief note for the producer"
}}"""

        return await self._generate_json(prompt, temperature=0.6)
