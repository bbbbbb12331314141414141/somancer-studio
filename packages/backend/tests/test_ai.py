"""Tests for AI endpoints (mocked Ollama)."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from aimusic.main import app
from aimusic.db import get_db, SessionLocal
from aimusic.models.entities import Base, engine


@pytest.fixture(scope="function")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_db):
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_ai_health_ollama_down(client):
    """When Ollama is unreachable, health returns available=False."""
    with patch(
        "aimusic.api.ai.OllamaService.is_available",
        new_callable=AsyncMock,
        return_value=False,
    ):
        response = client.get("/api/v1/ai/health")
        assert response.status_code == 200
        assert response.json()["available"] is False


def test_ai_health_ollama_up(client):
    """When Ollama is up, health returns available=True."""
    with (
        patch("aimusic.api.ai.OllamaService.is_available", new_callable=AsyncMock, return_value=True),
        patch("aimusic.api.ai.OllamaService.list_models", new_callable=AsyncMock, return_value=[
            {"name": "mistral", "size": 4000000000}
        ]),
    ):
        response = client.get("/api/v1/ai/health")
        assert response.status_code == 200
        data = response.json()
        assert data["available"] is True
        assert data["model_count"] == 1


def test_generate_lyrics_ollama_unavailable(client):
    """Returns 503 when Ollama is down."""
    with patch(
        "aimusic.api.ai.OllamaService.is_available",
        new_callable=AsyncMock,
        return_value=False,
    ):
        response = client.post("/api/v1/ai/lyrics", json={
            "section": "verse",
            "count": 4,
            "genre": "pop",
            "mood": "happy",
        })
        assert response.status_code == 503


MOCK_LYRIC_JSON = """[
  {"line_number": 1, "section": "verse", "text": "Walking through the city lights", "mood": "hopeful"},
  {"line_number": 2, "section": "verse", "text": "Every star above me shines so bright", "mood": "hopeful"},
  {"line_number": 3, "section": "verse", "text": "I feel the rhythm in my soul tonight", "mood": "hopeful"},
  {"line_number": 4, "section": "verse", "text": "Dancing on the edge of something right", "mood": "hopeful"}
]"""


def test_generate_lyrics_success(client):
    """Successfully generate lyrics via mocked Ollama."""
    with (
        patch("aimusic.api.ai.OllamaService.is_available", new_callable=AsyncMock, return_value=True),
        patch("aimusic.services.ollama_service.OllamaService.generate", new_callable=AsyncMock, return_value=MOCK_LYRIC_JSON),
    ):
        response = client.post("/api/v1/ai/lyrics", json={
            "section": "verse",
            "count": 4,
            "genre": "pop",
            "mood": "hopeful",
            "theme": "night",
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["lines"]) == 4
        assert data["agent"] == "songwriter"
        assert data["lines"][0]["section"] == "verse"
        assert len(data["lines"][0]["text"]) > 0


MOCK_CHORD_JSON = '{"progression": ["Cm", "Ab", "Eb", "Bb"], "bars_per_chord": [2, 2, 2, 2]}'
MOCK_PLAN_JSON = '{"chord_progression": ["Cm", "Ab", "Eb", "Bb"], "bars_per_chord": [2,2,2,2], "structure": ["verse","chorus"], "rhythmic_feel": "straight"}'
MOCK_NOTES_JSON = '{"notes": [{"pitch": 60, "start": 0.0, "duration": 1.0, "velocity": 80}, {"pitch": 62, "start": 1.0, "duration": 0.5, "velocity": 75}]}'


def test_compose_ollama_unavailable(client):
    """Returns 503 when Ollama is down."""
    with patch("aimusic.api.ai.OllamaService.is_available", new_callable=AsyncMock, return_value=False):
        response = client.post("/api/v1/ai/compose", json={
            "genre": "pop", "mood": "happy", "key": "C Major", "bpm": 120, "bars": 4,
        })
        assert response.status_code == 503


def test_generate_chords(client):
    """Successfully get chord progression."""
    with (
        patch("aimusic.api.ai.OllamaService.is_available", new_callable=AsyncMock, return_value=True),
        patch("aimusic.services.ollama_service.OllamaService.generate", new_callable=AsyncMock, return_value=MOCK_CHORD_JSON),
    ):
        response = client.get("/api/v1/ai/chords?key=C+Minor&genre=neo-soul&mood=romantic&bars=4")
        assert response.status_code == 200
        data = response.json()
        assert "chord_progression" in data
        assert len(data["chord_progression"]) > 0
