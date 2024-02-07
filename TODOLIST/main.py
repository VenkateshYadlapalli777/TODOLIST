import models
from models import ToDos
from database import engine,SessionLocal
from fastapi import FastAPI,Depends,status,Path
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel,Field
from routers import auth,todos


app = FastAPI()

models.Base.metadata.create_all(bind = engine)

app.include_router(auth.router)
app.include_router(todos.router)

