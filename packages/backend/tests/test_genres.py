"""Tests for genre endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

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


def test_list_genres_empty(client):
    response = client.get("/api/v1/genres/")
    assert response.status_code == 200
    data = response.json()
    assert data["genres"] == []
    assert data["total"] == 0


def test_create_genre(client):
    payload = {
        "name": "Rock",
        "description": "Guitar-driven music",
        "bpm_min": 80,
        "bpm_max": 160,
        "common_keys": ["E Major", "A Major"],
        "common_instruments": ["Guitar", "Bass", "Drums"],
        "production_techniques": ["Distortion"],
    }
    response = client.post("/api/v1/genres/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Rock"
    assert data["id"] is not None


def test_get_genre(client):
    payload = {"name": "Jazz", "bpm_min": 60, "bpm_max": 280}
    created = client.post("/api/v1/genres/", json=payload).json()
    response = client.get(f"/api/v1/genres/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Jazz"


def test_get_nonexistent_genre(client):
    response = client.get("/api/v1/genres/9999")
    assert response.status_code == 404


def test_search_genres(client):
    client.post("/api/v1/genres/", json={"name": "Ambient Electronic"})
    client.post("/api/v1/genres/", json={"name": "House"})
    response = client.get("/api/v1/genres/?search=ambient")
    assert response.status_code == 200
    data = response.json()
    assert any("Ambient" in g["name"] for g in data["genres"])


def test_create_subgenre(client):
    parent = client.post("/api/v1/genres/", json={"name": "Rock"}).json()
    child_payload = {"name": "Metal", "parent_id": parent["id"]}
    child = client.post("/api/v1/genres/", json=child_payload).json()
    assert child["parent_id"] == parent["id"]

    subs = client.get(f"/api/v1/genres/{parent['id']}/subgenres").json()
    assert any(g["name"] == "Metal" for g in subs)


def test_delete_genre(client):
    created = client.post("/api/v1/genres/", json={"name": "Temp"}).json()
    response = client.delete(f"/api/v1/genres/{created['id']}")
    assert response.status_code == 204
    response = client.get(f"/api/v1/genres/{created['id']}")
    assert response.status_code == 404
