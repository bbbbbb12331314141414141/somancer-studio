"""Tests for project endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from aimusic.main import app
from aimusic.db import SessionLocal, get_db
from aimusic.models.entities import Base, engine
from aimusic.schemas.project import ProjectCreate


# Setup test database
@pytest.fixture
def setup_db():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_db):
    """Provide database session for tests."""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Provide test client with database override."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_list_projects_empty(client):
    """Test listing projects when empty."""
    response = client.get("/api/v1/projects/")
    assert response.status_code == 200
    data = response.json()
    assert data["projects"] == []
    assert data["total"] == 0


def test_create_project(client):
    """Test creating a project."""
    project_data = {
        "name": "My Album",
        "project_type": "album",
        "genre": "Rock",
        "artist_name": "My Band",
        "bpm": 120,
        "key": "G Major",
    }
    response = client.post("/api/v1/projects/", json=project_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Album"
    assert data["project_type"] == "album"
    assert data["id"] is not None


def test_get_project(client):
    """Test getting a project."""
    # Create project first
    project_data = {"name": "Test Project", "project_type": "single"}
    create_response = client.post("/api/v1/projects/", json=project_data)
    project_id = create_response.json()["id"]

    # Get project
    response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["id"] == project_id


def test_get_nonexistent_project(client):
    """Test getting nonexistent project."""
    response = client.get("/api/v1/projects/999")
    assert response.status_code == 404


def test_update_project(client):
    """Test updating a project."""
    # Create project
    project_data = {"name": "Original Name", "project_type": "single"}
    create_response = client.post("/api/v1/projects/", json=project_data)
    project_id = create_response.json()["id"]

    # Update project
    update_data = {"name": "New Name"}
    response = client.patch(f"/api/v1/projects/{project_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"


def test_delete_project(client):
    """Test deleting a project."""
    # Create project
    project_data = {"name": "To Delete", "project_type": "single"}
    create_response = client.post("/api/v1/projects/", json=project_data)
    project_id = create_response.json()["id"]

    # Delete project
    response = client.delete(f"/api/v1/projects/{project_id}")
    assert response.status_code == 204

    # Verify deleted
    response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 404
