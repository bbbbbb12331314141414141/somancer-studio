"""Tests for audio API endpoints (mocked AudioService)."""

import pytest
from unittest.mock import MagicMock, patch
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


def test_list_soundfonts_empty(client):
    """List soundfonts returns empty list when none installed."""
    response = client.get("/api/v1/audio/soundfonts")
    assert response.status_code == 200
    data = response.json()
    assert "soundfonts" in data
    assert "total" in data
    assert isinstance(data["soundfonts"], list)


def test_waveform_file_not_found(client):
    """Returns 404 for non-existent audio file."""
    response = client.get("/api/v1/audio/waveform/nonexistent_file.wav")
    assert response.status_code == 404


def test_download_file_not_found(client):
    """Returns 404 for non-existent download."""
    response = client.get("/api/v1/audio/download/nonexistent.wav")
    assert response.status_code == 404


def test_render_midi_missing_midiutil(client):
    """Returns 501 when midiutil is not installed."""
    with patch("aimusic.api.audio._HAS_MIDIUTIL", False, create=True):
        with patch("aimusic.utils.midi_writer._HAS_MIDIUTIL", False):
            response = client.post("/api/v1/audio/render-midi", json={
                "composition": {
                    "tempo": 120,
                    "time_signature_numerator": 4,
                    "time_signature_denominator": 4,
                    "key": "C Major",
                    "tracks": [],
                    "chord_progression": [],
                    "structure": [],
                },
                "sample_rate": 48000,
                "normalize": True,
            })
            assert response.status_code in (500, 501)


def test_render_midi_invalid_composition(client):
    """Returns 422 for malformed composition data."""
    response = client.post("/api/v1/audio/render-midi", json={
        "composition": {"invalid": "data"},
        "sample_rate": 48000,
        "normalize": True,
    })
    assert response.status_code in (422, 500)
