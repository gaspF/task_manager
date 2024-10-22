import pytest
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models import Task
from api.database import Base
from api.crud import create_task, get_task, update_task, delete_task, get_tasks
from api.schemas import TaskCreate, TaskUpdate

# Configuration de la base de données pour les tests (SQLite en mémoire)
SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = sqlalchemy.orm.declarative_base()

@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_create_task(db_session):
    task_data = TaskCreate(title="Test Task", description="Test description")
    task = create_task(db=db_session, task=task_data)
    assert task.title == "Test Task"
    assert task.description == "Test description"
    assert task.completed is False

def test_get_task(db_session):
    task_data = TaskCreate(title="Test Task", description="Test description")
    created_task = create_task(db=db_session, task=task_data)
    
    task = get_task(db=db_session, task_id=created_task.id)
    assert task.id == created_task.id
    assert task.title == "Test Task"
    assert task.description == "Test description"

def test_update_task(db_session):
    task_data = TaskCreate(title="Test Task", description="Test description")
    created_task = create_task(db=db_session, task=task_data)
    
    update_data = TaskUpdate(completed=True)
    updated_task = update_task(db=db_session, task_id=created_task.id, task_update=update_data)
    
    assert updated_task.completed is True

def test_delete_task(db_session):
    task_data = TaskCreate(title="Test Task", description="Test description")
    created_task = create_task(db=db_session, task=task_data)
    
    delete_task(db=db_session, task_id=created_task.id)
    
    task = get_task(db=db_session, task_id=created_task.id)
    assert task is None

def test_get_tasks(db_session):
    task1 = TaskCreate(title="Task 1", description="Description 1")
    task2 = TaskCreate(title="Task 2", description="Description 2")
    
    create_task(db=db_session, task=task1)
    create_task(db=db_session, task=task2)
    
    tasks = get_tasks(db=db_session)
    
    assert len(tasks) == 2
    assert tasks[0].title == "Task 1"
    assert tasks[1].title == "Task 2"
