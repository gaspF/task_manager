from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from . import crud, schemas
from .models import Task

# Créer la base de données
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Créer une nouvelle tâche
@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task)

# Récupérer toutes les tâches
@app.get("/tasks/", response_model=list[schemas.Task])
def read_tasks(skip: int = 0, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db)
    return tasks

# Récupérer une tâche par ID
@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db=db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Mise à jour d'une tâche
@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    return crud.update_task(db=db, task_id=task_id, task_update=task)

# Suppression d'une tâche
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    crud.delete_task(db=db, task_id=task_id)
    return {"message": "Task deleted"}
