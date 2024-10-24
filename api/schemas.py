from pydantic import BaseModel


# Modèle de base pour une tâche
class TaskBase(BaseModel):
    title: str
    description: str


# Modèle pour la création d'une tâche
class TaskCreate(TaskBase):
    pass


# Modèle pour la mise à jour d'une tâche
class TaskUpdate(BaseModel):
    completed: bool


# Modèle pour retourner une tâche
class Task(TaskBase):
    id: int
    completed: bool = False

    class Config:
        from_attributes = True
