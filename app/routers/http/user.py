from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from mysqlx import Session
from model.user import UserModel
from service import get_current_user, signup_new
from db import get_db
from schemas import UserSignUp

user_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@user_router.get("/user/me")
async def get_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    return get_current_user(token=token)


@user_router.get("/get-users")
async def get_all_user(db: Session = Depends(get_db)):
    return db.query(UserModel).all()

@user_router.post("/signup")
async def signup(sign_up: UserSignUp, db: Session = Depends(get_db)):
    await signup_new(signup=sign_up, db=db)
    return JSONResponse(status_code=200, content="Sign up success")
