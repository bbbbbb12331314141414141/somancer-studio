"""Tests for the system API endpoints."""

import pytest
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


def test_system_info(client):
    """System info returns expected keys."""
    response = client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "python_version" in data
    assert "platform" in data
    assert "uptime_seconds" in data
    assert data["version"] == "0.8.0"


def test_health_detail(client):
    """Detailed health check returns status and components."""
    response = client.get("/api/v1/system/health/detail")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert "cache" in data
    assert "job_queue" in data
    assert "database" in data


def test_cache_stats(client):
    """Cache stats endpoint returns expected shape."""
    response = client.get("/api/v1/system/cache/stats")
    assert response.status_code == 200
    data = response.json()
    assert "size" in data
    assert "hits" in data
    assert "misses" in data
    assert "hit_rate" in data


def test_cache_purge(client):
    """Cache purge returns removed count."""
    response = client.post("/api/v1/system/cache/purge")
    assert response.status_code == 200
    data = response.json()
    assert "removed" in data
    assert isinstance(data["removed"], int)


def test_cache_clear(client):
    """Cache clear returns success."""
    response = client.post("/api/v1/system/cache/clear")
    assert response.status_code == 200
    assert response.json()["cleared"] is True


def test_cache_invalidate_prefix(client):
    """Cache invalidate prefix returns removed count."""
    response = client.post("/api/v1/system/cache/invalidate?prefix=genres:")
    assert response.status_code == 200
    data = response.json()
    assert "removed" in data
    assert data["prefix"] == "genres:"


def test_get_settings(client):
    """Settings endpoint returns application configuration."""
    response = client.get("/api/v1/system/settings")
    assert response.status_code == 200
    data = response.json()
    assert "audio_sample_rate" in data
    assert "ollama_host" in data
    assert "environment" in data
    assert "enable_ai" in data


def test_list_directories(client):
    """Directory listing returns expected structure."""
    response = client.get("/api/v1/system/directories")
    assert response.status_code == 200
    data = response.json()
    assert "directories" in data
    dirs = data["directories"]
    for name in ("projects", "exports", "plugins"):
        assert name in dirs
        assert "path" in dirs[name]
        assert "exists" in dirs[name]


def test_init_directories(client):
    """Init directories creates expected paths."""
    response = client.post("/api/v1/system/directories/init")
    assert response.status_code == 200
    data = response.json()
    assert "created" in data
    assert isinstance(data["created"], list)


def test_root_endpoint_version(client):
    """Root endpoint reports correct version."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["version"] == "0.8.0"


def test_health_endpoint_version(client):
    """Health endpoint reports v0.8.0."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["version"] == "0.8.0"
