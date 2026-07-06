"""
Songwriter Agent — AI-powered lyrics generation.

Generates verse, chorus, bridge, and other sections based on
genre, mood, theme, and vocabulary preferences.
"""

from dataclasses import dataclass, field
from typing import Optional

from aimusic.services.agents.base_agent import BaseAgent, AgentError


@dataclass
class LyricLine:
    """A single generated lyric line."""
    line_number: int
    section: str
    text: str
    mood: Optional[str] = None
    rhyme_scheme: Optional[str] = None


@dataclass
class LyricsGenerationInput:
    """Parameters for lyric generation."""
    section: str = "verse"                # verse | chorus | bridge | pre-chorus | outro | intro
    count: int = 4                        # number of lines
    genre: Optional[str] = None
    mood: Optional[str] = None            # happy | sad | romantic | angry | introspective…
    theme: Optional[str] = None           # love | loss | freedom | struggle…
    vocabulary: str = "poetic"            # simple | conversational | poetic | complex
    perspective: str = "first_person"     # first_person | second_person | third_person
    language: str = "en"
    length: str = "medium"               # short | medium | long (syllable guidance)
    rhyme: bool = True
    existing_lyrics: Optional[str] = None  # existing lines for continuity
    artist_name: Optional[str] = None


SONGWRITER_SYSTEM = """You are an expert lyricist and songwriter with deep knowledge of music across
all genres. You write emotionally resonant, original lyrics that avoid clichés. You understand
rhyme schemes, syllable stress, internal rhyme, and how lyrics sit within melodies.

You always respond with valid JSON only — no preamble, no explanation, no markdown."""


class SongwriterAgent(BaseAgent):
    """AI agent specialising in lyrics generation."""

    AGENT_NAME = "songwriter"
    SYSTEM_PROMPT = SONGWRITER_SYSTEM

    async def generate_lyrics(
        self,
        params: LyricsGenerationInput,
    ) -> list[LyricLine]:
        """
        Generate lyric lines based on the provided parameters.

        Returns a list of LyricLine objects.
        """
        prompt = self._build_prompt(params)
        raw = await self._generate_json(prompt, temperature=0.85)

        # Parse list of line objects
        if isinstance(raw, list):
            lines_data = raw
        elif isinstance(raw, dict) and "lines" in raw:
            lines_data = raw["lines"]
        else:
            raise AgentError(f"Unexpected JSON shape from songwriter: {type(raw)}")

        lines: list[LyricLine] = []
        for i, item in enumerate(lines_data):
            if isinstance(item, str):
                lines.append(LyricLine(
                    line_number=i + 1,
                    section=params.section,
                    text=item.strip(),
                    mood=params.mood,
                ))
            elif isinstance(item, dict):
                lines.append(LyricLine(
                    line_number=item.get("line_number", i + 1),
                    section=item.get("section", params.section),
                    text=item.get("text", "").strip(),
                    mood=item.get("mood", params.mood),
                    rhyme_scheme=item.get("rhyme_scheme"),
                ))

        return lines

    async def continue_lyrics(
        self,
        existing: list[str],
        params: LyricsGenerationInput,
    ) -> list[LyricLine]:
        """Continue existing lyrics, maintaining style and narrative."""
        params.existing_lyrics = "\n".join(existing)
        params.count = max(2, params.count)
        return await self.generate_lyrics(params)

    async def rewrite_lyrics(
        self,
        original: str,
        mood: Optional[str] = None,
        vocabulary: str = "poetic",
        genre: Optional[str] = None,
    ) -> list[LyricLine]:
        """Rewrite existing lyrics with a different mood or style."""
        prompt = f"""Rewrite the following lyrics while preserving the core meaning.
New mood: {mood or 'same as original'}
Vocabulary style: {vocabulary}
Genre context: {genre or 'unspecified'}

Original lyrics:
{original}

Respond with a JSON array of objects: [{{"line_number": 1, "text": "..."}}]"""

        raw = await self._generate_json(prompt, temperature=0.75)
        lines_data = raw if isinstance(raw, list) else raw.get("lines", [])

        return [
            LyricLine(
                line_number=item.get("line_number", i + 1),
                section="verse",
                text=item.get("text", "").strip(),
                mood=mood,
            )
            for i, item in enumerate(lines_data)
            if isinstance(item, dict)
        ]

    # ── Private ───────────────────────────────────────────────────────────────

    def _build_prompt(self, p: LyricsGenerationInput) -> str:
        syllable_hint = {
            "short": "6–8 syllables per line",
            "medium": "8–12 syllables per line",
            "long": "12–16 syllables per line",
        }.get(p.length, "8–12 syllables per line")

        perspective_hint = {
            "first_person": "Use 'I', 'me', 'my'",
            "second_person": "Use 'you', 'your'",
            "third_person": "Use 'he', 'she', 'they'",
        }.get(p.perspective, "Use 'I', 'me', 'my'")

        existing_block = ""
        if p.existing_lyrics:
            existing_block = f"""
Existing lyrics for context and continuity:
{p.existing_lyrics}

Continue in the same style."""

        return f"""Write {p.count} original {p.section} lines for a {p.genre or 'pop'} song.

Context:
- Section: {p.section}
- Mood: {p.mood or 'neutral'}
- Theme: {p.theme or 'open'}
- Vocabulary: {p.vocabulary}
- Perspective: {perspective_hint}
- Length guidance: {syllable_hint}
- Rhyme: {'yes, use AABB or ABAB scheme' if p.rhyme else 'free verse, no forced rhyme'}
- Language: {p.language}
{existing_block}

Rules:
1. Be original — avoid clichés
2. Match the {p.mood or 'neutral'} mood authentically
3. Lines should flow naturally when sung
4. Do NOT include section labels in the text

Respond ONLY with a JSON array:
[
  {{"line_number": 1, "section": "{p.section}", "text": "...", "mood": "{p.mood or 'neutral'}"}},
  {{"line_number": 2, "section": "{p.section}", "text": "...", "mood": "{p.mood or 'neutral'}"}}
]"""
