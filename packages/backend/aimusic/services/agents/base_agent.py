"""
Base Agent — shared logic for all Sonmancer AI agents.

All agents inherit from BaseAgent, which provides:
- Ollama client access
- Structured JSON response parsing
- Prompt templating helpers
- Error handling & retries
"""

import json
import logging
import re
from typing import Any

from aimusic.services.ollama_service import OllamaService, OllamaError

logger = logging.getLogger(__name__)

# Default model used when caller doesn't specify one
DEFAULT_MODEL = "mistral"


class AgentError(Exception):
    """Raised when an agent cannot complete its task."""


class BaseAgent:
    """Base class for all Sonmancer AI agents."""

    # Override in subclasses
    AGENT_NAME: str = "base"
    SYSTEM_PROMPT: str = "You are a helpful AI assistant."

    def __init__(
        self,
        ollama: OllamaService,
        model: str = DEFAULT_MODEL,
    ) -> None:
        self.ollama = ollama
        self.model = model

    # ── Internal helpers ──────────────────────────────────────────────────────

    async def _generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.8,
    ) -> str:
        """Run a generation with this agent's model and system prompt."""
        try:
            return await self.ollama.generate(
                prompt=prompt,
                model=self.model,
                system=system or self.SYSTEM_PROMPT,
                temperature=temperature,
            )
        except OllamaError as exc:
            raise AgentError(f"[{self.AGENT_NAME}] Ollama error: {exc}") from exc

    async def _generate_json(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        retries: int = 2,
    ) -> Any:
        """
        Generate text and parse it as JSON.
        Retries up to `retries` times on parse failure.
        """
        last_err: Exception | None = None
        for attempt in range(retries + 1):
            try:
                raw = await self._generate(
                    prompt=prompt,
                    system=system or self.SYSTEM_PROMPT,
                    temperature=temperature,
                )
                return self._extract_json(raw)
            except (json.JSONDecodeError, AgentError) as exc:
                last_err = exc
                logger.warning(
                    f"[{self.AGENT_NAME}] JSON parse attempt {attempt + 1} failed: {exc}"
                )
        raise AgentError(
            f"[{self.AGENT_NAME}] Could not parse JSON after {retries + 1} attempts"
        ) from last_err

    @staticmethod
    def _extract_json(text: str) -> Any:
        """
        Extract the first JSON object or array from arbitrary text.
        Handles responses wrapped in markdown code fences.
        """
        # Strip markdown code fences
        text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("```").strip()

        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find a JSON block with regex
        for pattern in (r"\{.*\}", r"\[.*\]"):
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass

        raise json.JSONDecodeError("No valid JSON found", text, 0)

    @staticmethod
    def _build_context(**kwargs: Any) -> str:
        """Build a context block from keyword arguments for inclusion in prompts."""
        parts = []
        for key, value in kwargs.items():
            if value is not None:
                label = key.replace("_", " ").title()
                parts.append(f"{label}: {value}")
        return "\n".join(parts)
