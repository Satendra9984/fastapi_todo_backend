
from datetime import datetime, timedelta
from pydantic import Field, BaseModel
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt

router = APIRouter(
   prefix='/auth',
   tags=['auth']
)

SECRET_KEY = '0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')



# ORM Model for getting userinput in proper format
class UserRequest(BaseModel):
    username:str
    email:str 
    first_name:str = Field(min_length=2, max_length=30) 
    last_name:str = Field(min_length=2, max_length=30) 
    password:str = Field(min_length=6) 
    role: str 

class Token(BaseModel):
    access_token:str
    token_type:str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

async def create_access_token(username:str, userid:str, timedelta: timedelta):
    encode = {'sub': username, 'id': userid}
    expiry = datetime.utcnow() + timedelta
    encode.update({'exp': expiry})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth_bearer)]):
    try:
        payload = jwt.decode(token=token, algorithms=[ALGORITHM], key=SECRET_KEY)
        username:str = payload.get('sub')
        user_id:str = payload.get('id')
        role:str = payload.get('role')

        if user_id is None and username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Credentials')
        return {'username': username, 'id': user_id, 'role': role}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Credentials')

 
async def authenticate_user(username: str, passoword: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user or user is None:
        return False
    if not bcrypt_context.verify(passoword, user.hashed_password):
        return False
    return user

# function for hashing passwords
@router.post("/token", response_model=Token)
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db:db_dependency ):
    authed = await authenticate_user(username=form_data.username,passoword= form_data.password, db=db)
    if not authed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Credentials')
    
    token = await create_access_token(username=authed.username, userid=authed.id, timedelta=timedelta(minutes=20))
    
    return {
        'access_token': token,
        'token_type': 'bearer'
    }


@router.get("/get_all", status_code=status.HTTP_200_OK)
async def get_user(db: db_dependency):
    return db.query(User).all()



@router.post("/add_user", status_code=status.HTTP_201_CREATED)
async def add_user(db:db_dependency, user_request: UserRequest):
    try:
        user = User(
        username=user_request.username,
        email=user_request.email,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=bcrypt_context.hash(secret=user_request.password),
        is_active=True,
        user_role=user_request.role
    )

        db.add(user)
        db.commit()
    except Exception as exp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Something went wrong {exp.args}')


