from typing import Annotated
from passlib.context import CryptContext

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.util import deprecated
from starlette import status

from database import SessionLocal
from models import Users

router = APIRouter()
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class CreateUser(BaseModel):
    username: str
    email: str
    firstname: str
    lastname: str
    password: str
    role: str


@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user: CreateUser):
    created_user = Users(
        email=user.email,
        username=user.username,
        firstname=user.firstname,
        lastname=user.lastname,
        role=user.role,
        hashed_password=bcrypt_context.hash(user.password),
        is_active=True
    )
    db.add(created_user)
    db.commit()

@router.get("/auth")
async def get_users(db: db_dependency):
    if not None:
        return db.query(Users).all()
    else:
        return "Nothing Here"
