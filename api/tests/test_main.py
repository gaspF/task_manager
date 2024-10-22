import pytest
import sqlalchemy
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = sqlalchemy.orm.declarative_base()

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

sample_task = {"title": "Test Task", "description": "This is a test task"}

def test_create_task():
    response = client.post("/tasks/", json=sample_task)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == sample_task["title"]
    assert data["description"] == sample_task["description"]
    assert "id" in data

def test_read_task():
    response = client.post("/tasks/", json=sample_task)
    task_id = response.json()["id"]
    
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == sample_task["title"]
    assert data["description"] == sample_task["description"]

def test_update_task():
    response = client.post("/tasks/", json=sample_task)
    task_id = response.json()["id"]

    update_data = {"completed": True}
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["completed"] is True

def test_delete_task():
    response = client.post("/tasks/", json=sample_task)
    task_id = response.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Task deleted"}

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}