"""Tests for mixing, mastering, and vocal synthesis endpoints."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
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
    def override():
        yield db_session
    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_list_platform_targets(client):
    """Platform loudness targets endpoint returns data."""
    response = client.get("/api/v1/mix/platforms")
    assert response.status_code == 200
    data = response.json()
    assert "platforms" in data
    names = [p["name"] for p in data["platforms"]]
    assert "spotify" in names
    assert "apple_music" in names


def test_list_vocal_engines(client):
    """Vocal engines list includes known engines."""
    response = client.get("/api/v1/mix/vocals/engines")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    names = [e["name"] for e in data]
    assert "tts_stub" in names
    assert "diffsinger" in names


def test_phoneme_conversion(client):
    """Phoneme conversion returns result for English text."""
    response = client.post(
        "/api/v1/mix/vocals/phonemes",
        params={"text": "I love the night sky", "section": "chorus"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "phonemes" in data
    assert data["count"] > 0


def test_mix_plan_ollama_down(client):
    """Returns 503 when Ollama is unavailable."""
    with patch(
        "aimusic.api.mixing.OllamaService.is_available",
        new_callable=AsyncMock, return_value=False
    ):
        response = client.post("/api/v1/mix/plan", json={
            "genre": "neo-soul",
            "mood": "romantic",
            "tracks": [
                {"name": "Piano", "instrument": "piano"},
                {"name": "Bass",  "instrument": "bass"},
                {"name": "Drums", "instrument": "drums"},
            ],
        })
        assert response.status_code == 503


def test_mastering_chain_ollama_down(client):
    """Returns 503 when Ollama is unavailable."""
    with patch(
        "aimusic.api.mixing.OllamaService.is_available",
        new_callable=AsyncMock, return_value=False
    ):
        response = client.post("/api/v1/mix/master", json={
            "genre": "pop", "mood": "happy", "platform": "spotify",
        })
        assert response.status_code == 503


MOCK_MIX_JSON = """{
  "mix_notes": "Keep the low mids clean.",
  "master_buss_eq": [
    {"frequency": 100, "gain_db": -1.5, "q": 0.7, "filter_type": "lowshelf"}
  ],
  "tracks": [
    {
      "track_name": "Piano", "instrument": "piano",
      "volume_db": -6.0, "pan": 0.1,
      "eq_bands": [{"frequency": 200, "gain_db": -2.0, "q": 1.2, "filter_type": "peak"}],
      "compressor": {
        "threshold_db": -18, "ratio": 3.0, "attack_ms": 10,
        "release_ms": 150, "makeup_gain_db": 4.0, "knee_db": 6.0
      },
      "reverb_send": 0.3, "delay_send": 0.1,
      "notes": "Light EQ cut around 200Hz"
    }
  ]
}"""


def test_mix_plan_success(client):
    """Successfully generate a mix plan with mocked Ollama."""
    with (
        patch("aimusic.api.mixing.OllamaService.is_available",
              new_callable=AsyncMock, return_value=True),
        patch("aimusic.services.ollama_service.OllamaService.generate",
              new_callable=AsyncMock, return_value=MOCK_MIX_JSON),
    ):
        response = client.post("/api/v1/mix/plan", json={
            "genre": "neo-soul",
            "mood": "romantic",
            "tracks": [{"name": "Piano", "instrument": "piano"}],
        })
        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "mix_engineer"
        assert len(data["tracks"]) == 1
        assert data["tracks"][0]["track_name"] == "Piano"


def test_vocal_synthesis_no_lyrics(client):
    """Returns 422 when no lyrics provided."""
    response = client.post("/api/v1/mix/vocals/synthesise", json={
        "lyrics": [], "bpm": 120.0, "engine": "tts_stub"
    })
    assert response.status_code == 422


def test_stem_export_missing_midiutil(client):
    """Returns 501 when midiutil not installed."""
    with patch("aimusic.api.mixing._HAS_MIDIUTIL", False, create=True):
        with patch("aimusic.utils.midi_writer._HAS_MIDIUTIL", False):
            response = client.post("/api/v1/mix/stems/export", json={
                "composition": {
                    "tempo": 120,
                    "time_signature_numerator": 4,
                    "time_signature_denominator": 4,
                    "key": "C Major",
                    "tracks": [],
                    "chord_progression": [],
                    "structure": [],
                },
            })
            assert response.status_code in (500, 501)
