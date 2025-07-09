from datetime import timedelta, datetime, timezone
from os import getenv
from typing import Annotated
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Users
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv

router = APIRouter(
    prefix="/auth",
    tags=['auth']
)

'''
DEPENDENCIES
'''
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

load_dotenv()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

'''
some regular python functions
'''
# get user from DB by username
def authenticate_uer(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, id: int, expires_delta: timedelta):
    expires = datetime.now(timezone.utc) + expires_delta
    encode = {"sub": username, "id": id, "exp": expires}
    return jwt.encode(encode, getenv("SECRET_KEY"), algorithm=getenv("ALGORITHM"))

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, getenv("SECRET_KEY"), algorithms=[getenv("ALGORITHM")])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if not username or not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate user!!!")

'''
CLASSES
'''
class CreateUser(BaseModel):
    username: str
    email: str
    firstname: str
    lastname: str
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str


'''
API ENDPOINTS
'''
@router.post("/", status_code=status.HTTP_201_CREATED)
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

@router.get("/")
async def get_users(db: db_dependency):
    if not None:
        return db.query(Users).all()
    else:
        return "Nothing Here"


@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_uer(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")

    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}
