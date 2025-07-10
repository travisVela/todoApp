
from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Todos, TodosRequest, Users, UserRequest
from database import SessionLocal
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix="/users",
    tags=['users']
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
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)

'''
API ENDPOINTS
'''

@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Authorization failed")
    return db.query(Users).filter(Users.id == user.get("id")).first()

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    auth_user = db.query(Users).filter(Users.id == user.get("id")).first()
    if not bcrypt_context.verify(user_verification.password, auth_user.hashed_password):
        raise HTTPException(status_code=401, detail="Error resetting password")

    auth_user.hashed_password = bcrypt_context.hash(user_verification.new_password)

    db.add(auth_user)
    db.commit()

@router.put("/phonenumber/{num}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, num: str):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    auth_user = db.query(Users).filter(Users.id == user.get("id")).first()

    auth_user.phone_number = num

    db.add(auth_user)
    db.commit()





