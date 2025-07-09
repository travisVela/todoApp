from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Todos, TodosRequest, UserRequest, Users
from database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=['admin']
)


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

@router.get("/todo", status_code=status.HTTP_200_OK)
async def get_all(user: user_dependency, db: db_dependency):
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Not Authorized")
    return db.query(Todos).all()


@router.put("/user/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(user: user_dependency, db: db_dependency, id: int, user_request: UserRequest):
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Not Authorized")
    user_to_update = db.query(Users).filter(Users.id == id).first()

    user_to_update.firstname = user_request.firstname
    user_to_update.lastname = user_request.lastname
    user_to_update.role = user_request.role
    db.add(user_to_update)
    db.commit()

@router.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Not Authorized")
    trash = db.query(Todos).filter(Todos.id == id).first()

    if not trash:
        raise HTTPException(status_code=401, detail="Item not found")
    db.delete(trash)
    db.commit()
