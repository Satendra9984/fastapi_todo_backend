from pydantic import BaseModel, Field
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from database import SessionLocal
from models import Todo
from starlette import status
from .auth import get_current_user


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  

class TodoRequest(BaseModel):
    title:str = Field(min_length=3, max_length=50),
    description:str = Field( min_length=5, max_length=100),
    priority:int = Field( gt=0, lt=6)
    complete:bool 

    
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/get_todos")
async def read_all(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not authorized')

    return db.query(Todo).filter(Todo.user_id == user.get('id')).all()


@router.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def read_todo(user:user_dependency,db:db_dependency,todo_id: int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not authorized')

    todo_model = db.query(Todo).filter(Todo.id==todo_id).filter(Todo.user_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found')


@router.post("/add_todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,  db:db_dependency, todo: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not authorized')

    try:
        todo = Todo(**todo.model_dump(), user_id=user.get('id'))
        db.add(todo)
        db.commit()
    except Exception as exp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'User not authorized {exp.args}')
