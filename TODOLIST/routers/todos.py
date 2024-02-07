import models
from models import ToDos
from database import engine,SessionLocal
from fastapi import APIRouter,Depends,status,Path
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel,Field
from routers import auth
from .auth import get_current_user

router = APIRouter()

def get_db():
    db= SessionLocal()
    try:
        yield db


    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class ToDoRequest(BaseModel):
    title : str = Field(min_length = 3)
    description: str = Field(min_length = 3, max_length = 100)
    priority : str = Field(max_length = 2)
    complete : bool

@router.get("/")
async def read_all(db: db_dependency):
    return db.query(ToDos).all()


@router.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def read_with_id(db: db_dependency,todo_id : int= Path(gt=0)):
    todo_id_model = db.query(ToDos).filter(ToDos.Id == todo_id).first()
    if todo_id_model is not None:
        return todo_id_model
    raise HTTPException(status_code = 404, details = 'ID not found')

@router.post("/todo/",status_code=status.HTTP_201_CREATED)
async def write_todo(user: user_dependency,db: db_dependency, todo_item: ToDoRequest):
    if user is None:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "unaithorized access")
    todo_model = ToDos(**todo_item.dict(), owner_id = user.get('Id'))

    db.add(todo_model)
    db.commit()

@router.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_id : int, todorequest : ToDoRequest):
    todo_model = db.query(ToDos).filter(ToDos.Id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code = 404, detail = "Id not found")

    todo_model.title = todorequest.title
    todo_model.description = todorequest.description
    todo_model.priority = todorequest.priority
    todo_model.complete = todorequest.complete

    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async  def delete_todo(db: db_dependency, todo_id : int):
    todo_model = db.query(ToDos).filter(ToDos.Id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Id not found")

    db.query(ToDos).filter(ToDos.Id == todo_id).delete()
    db.commit()

