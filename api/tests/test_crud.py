import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.database import Base
from api.crud import create_task, get_task, update_task, delete_task, get_tasks
from api.schemas import TaskCreate, TaskUpdate

TEST_DATABASE_URL = (
    "postgresql://postgres:mysecretpassword@db_test:5432/tasks_test_db"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


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
    updated_task = update_task(
        db=db_session, task_id=created_task.id, task_update=update_data
    )

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

    assert len(tasks) == 5
    assert tasks[3].title == "Task 1"
    assert tasks[4].title == "Task 2"
