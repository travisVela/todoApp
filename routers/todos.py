from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Todos, TodosRequest
from database import SessionLocal
from .auth import get_current_user

router = APIRouter()

'''
DEPENDENCIES
'''

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

'''
API ENDPOINTS
'''
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get("/todo/{id}", status_code=status.HTTP_200_OK)
async def get_by_id(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo = db.query(Todos).filter(Todos.owner_id == user.get("id")).filter(Todos.id == id).first()
    if todo:
        return todo
    raise HTTPException(status_code=404, detail="Item not found")

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo( user: user_dependency, db: db_dependency, todo: TodosRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo = Todos(**todo.model_dump(), owner_id=user.get("id"))

    db.add(todo)
    db.commit()

@router.put("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodosRequest, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo = db.query(Todos).filter(Todos.id == id).filter(Todos.owner_id == user.get("id")).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Item not found")

    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.complete = todo_request.complete

    db.add(todo)
    db.commit()

@router.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo = db.query(Todos).filter(Todos.id == id).filter(Todos.owner_id == user.get("id")).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Item not found")
    # db.query(Todos).filter(Todos.id == id).delete()
    db.delete(todo)
    db.commit()


