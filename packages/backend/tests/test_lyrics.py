"""Tests for lyrics endpoints."""

import pytest
from fastapi.testclient import TestClient

from aimusic.main import app
from aimusic.db import SessionLocal, get_db
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


@pytest.fixture
def project_and_song(client):
    """Create a project and song for tests."""
    project = client.post("/api/v1/projects/", json={"name": "Test Album", "project_type": "album"}).json()
    song = client.post("/api/v1/songs/", json={"name": "Test Song", "project_id": project["id"]}).json()
    return project, song


def test_list_lyrics_empty(client, project_and_song):
    _, song = project_and_song
    response = client.get(f"/api/v1/lyrics/?song_id={song['id']}")
    assert response.status_code == 200
    assert response.json()["lyrics"] == []


def test_create_lyrics(client, project_and_song):
    _, song = project_and_song
    payload = {
        "song_id": song["id"],
        "line_number": 1,
        "section": "verse",
        "text": "I am wandering through the night",
        "mood": "introspective",
    }
    response = client.post("/api/v1/lyrics/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "I am wandering through the night"
    assert data["section"] == "verse"


def test_update_lyrics(client, project_and_song):
    _, song = project_and_song
    created = client.post("/api/v1/lyrics/", json={
        "song_id": song["id"],
        "line_number": 1,
        "section": "chorus",
        "text": "Original text",
    }).json()

    response = client.patch(f"/api/v1/lyrics/{created['id']}", json={"text": "Updated text"})
    assert response.status_code == 200
    assert response.json()["text"] == "Updated text"


def test_filter_lyrics_by_section(client, project_and_song):
    _, song = project_and_song
    client.post("/api/v1/lyrics/", json={"song_id": song["id"], "line_number": 1, "section": "verse", "text": "V1"})
    client.post("/api/v1/lyrics/", json={"song_id": song["id"], "line_number": 2, "section": "chorus", "text": "C1"})

    response = client.get(f"/api/v1/lyrics/?song_id={song['id']}&section=verse")
    assert response.status_code == 200
    data = response.json()
    assert all(l["section"] == "verse" for l in data["lyrics"])


def test_delete_lyrics(client, project_and_song):
    _, song = project_and_song
    created = client.post("/api/v1/lyrics/", json={
        "song_id": song["id"],
        "line_number": 1,
        "section": "verse",
        "text": "To be deleted",
    }).json()

    response = client.delete(f"/api/v1/lyrics/{created['id']}")
    assert response.status_code == 204

    response = client.get(f"/api/v1/lyrics/{created['id']}")
    assert response.status_code == 404
