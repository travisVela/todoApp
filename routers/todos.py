from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Todos, TodosRequest
from database import SessionLocal

router = APIRouter()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency):
    if not None:
        return db.query(Todos).all()
    else:
        return "Nothing Here"

@router.get("/todo/{id}", status_code=status.HTTP_200_OK)
async def get_by_id(db: db_dependency, id: int = Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == id).first()
    if todo:
        return todo
    raise HTTPException(status_code=404, detail="Item not found")

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo: TodosRequest):
    todo = Todos(**todo.model_dump())

    db.add(todo)
    db.commit()

@router.put("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_request: TodosRequest, id: int = Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Item not found")

    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.complete = todo_request.complete

    db.add(todo)
    db.commit()

@router.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, id: int = Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Item not found")
    # db.query(Todos).filter(Todos.id == id).delete()
    db.delete(todo)
    db.commit()


