"""
Ollama Service — local LLM inference client.

Handles model management, prompt routing, streaming responses,
and context management for all AI agents.
"""

import json
import logging
from typing import AsyncIterator, Optional
import httpx

from aimusic.config import settings

logger = logging.getLogger(__name__)

# ── Default generation parameters ────────────────────────────────────────────

DEFAULT_TEMPERATURE = 0.8
DEFAULT_TOP_P       = 0.9
DEFAULT_NUM_CTX     = 4096

# ── Models known to work well for music tasks ────────────────────────────────

RECOMMENDED_MODELS = [
    "mistral",
    "gemma2",
    "llama3.2",
    "qwen2.5",
    "deepseek-r1",
]


class OllamaError(Exception):
    """Raised when Ollama returns an error or is unreachable."""


class OllamaService:
    """Client for Ollama local inference."""

    def __init__(self, host: str | None = None) -> None:
        self.host = (host or settings.ollama_host).rstrip("/")
        self._client = httpx.AsyncClient(timeout=120.0)

    # ── Health ────────────────────────────────────────────────────────────────

    async def is_available(self) -> bool:
        """Return True when Ollama is reachable."""
        try:
            resp = await self._client.get(f"{self.host}/api/tags", timeout=5.0)
            return resp.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[dict]:
        """Return list of locally available models."""
        try:
            resp = await self._client.get(f"{self.host}/api/tags")
            resp.raise_for_status()
            return resp.json().get("models", [])
        except httpx.HTTPError as exc:
            raise OllamaError(f"Failed to list models: {exc}") from exc

    async def pull_model(self, model: str) -> None:
        """Pull a model (blocking until complete)."""
        logger.info(f"Pulling model: {model}")
        try:
            async with self._client.stream(
                "POST",
                f"{self.host}/api/pull",
                json={"name": model},
                timeout=600.0,
            ) as resp:
                async for line in resp.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if data.get("status"):
                            logger.info(f"  {data['status']}")
        except httpx.HTTPError as exc:
            raise OllamaError(f"Failed to pull model: {exc}") from exc

    # ── Generation ────────────────────────────────────────────────────────────

    async def generate(
        self,
        prompt: str,
        model: str = "mistral",
        system: str | None = None,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = DEFAULT_TOP_P,
        num_ctx: int = DEFAULT_NUM_CTX,
    ) -> str:
        """Generate a non-streaming text completion."""
        payload: dict = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_ctx": num_ctx,
            },
        }
        if system:
            payload["system"] = system

        try:
            resp = await self._client.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=120.0,
            )
            resp.raise_for_status()
            return resp.json()["response"]
        except httpx.HTTPError as exc:
            raise OllamaError(f"Generation failed: {exc}") from exc

    async def stream_generate(
        self,
        prompt: str,
        model: str = "mistral",
        system: str | None = None,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> AsyncIterator[str]:
        """Generate a streaming text completion, yielding chunks."""
        payload: dict = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": temperature},
        }
        if system:
            payload["system"] = system

        try:
            async with self._client.stream(
                "POST",
                f"{self.host}/api/generate",
                json=payload,
                timeout=120.0,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line:
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            yield token
                        if chunk.get("done"):
                            break
        except httpx.HTTPError as exc:
            raise OllamaError(f"Streaming failed: {exc}") from exc

    async def chat(
        self,
        messages: list[dict],
        model: str = "mistral",
        system: str | None = None,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> str:
        """Multi-turn chat completion."""
        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if system:
            payload["system"] = system

        try:
            resp = await self._client.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=120.0,
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"]
        except httpx.HTTPError as exc:
            raise OllamaError(f"Chat failed: {exc}") from exc

    async def __aenter__(self) -> "OllamaService":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self._client.aclose()
