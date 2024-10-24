import os
import pytest
import sqlalchemy
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config
from api.main import app, get_db
from api.models import Base

TEST_DATABASE_URL = "postgresql://postgres:mysecretpassword@db_test:5432/tasks_test_db"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def db_session(setup_db):
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


sample_task = {"title": "Test Task", "description": "This is a very very test task"}


def test_create_task(client):
    response = client.post("/tasks/", json=sample_task)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == sample_task["title"]
    assert data["description"] == sample_task["description"]
    assert "id" in data


def test_read_task(client):
    response = client.post("/tasks/", json=sample_task)
    task_id = response.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == sample_task["title"]
    assert data["description"] == sample_task["description"]


def test_update_task(client):
    response = client.post("/tasks/", json=sample_task)
    task_id = response.json()["id"]

    update_data = {"completed": True}
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["completed"] is True


def test_delete_task(client):
    response = client.post("/tasks/", json=sample_task)
    task_id = response.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Task deleted"}

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}
