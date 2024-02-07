from pydantic import BaseModel,Field
from models import Users
from passlib.context import CryptContext
from typing import Annotated
from database import engine,SessionLocal
from fastapi import APIRouter,Depends,status,Path
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta,datetime

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "e8621be810f31d515d93db2c7f23618ca97535b1c8387d5a1572312973143ee3"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated = 'auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="aurh/token")

def get_db():
    db= SessionLocal()
    try:
        yield db


    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class UserRequest(BaseModel):
    email: str
    username:str
    first_name:str
    last_name:str
    hashed_password : str
    role : str


class Token(BaseModel):
    access_token : str
    token_type: str



def authenticate_user(username,password,db):
     user = db.query(Users).filter(Users.username==username).first()
     if not user:
         return False
     if not bcrypt_context.verify(password,user.hashed_password):
         return False
     return user

def create_access_token(username: str, user_id : int, expire_delta: timedelta):

    encode = {'sub':username, 'id': user_id}
    expires = datetime.utcnow() + expire_delta
    encode.update({'exp': expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username = payload.get('sub')
        user_id = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail ="Invalid token")
        return { 'username' : username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail ="Invalid token")





@router.post("/create_user/")
async def create_user(db: db_dependency,user_Request : UserRequest):
    user_request_model = Users(
        email = user_Request.email,
        username = user_Request.username,
        first_name = user_Request.first_name,
        last_name = user_Request.last_name,
        role = user_Request.role,
        hashed_password = bcrypt_context.hash(user_Request.hashed_password),
        is_active = True
    )

    db.add(user_request_model)
    db.commit()


@router.post("/token",response_model=Token)
async def login_with_access_token(form_data : Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dependency):
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail="could not validate user")

    token = create_access_token(user.username,user.Id,timedelta(minutes=20))
    return { 'access_token': token, 'token_type': "bearer"}
