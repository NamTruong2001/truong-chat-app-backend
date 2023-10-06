from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from dependencies import auth_service, user_service, participant_service
from schemas import UserSignUp, UserInformationResponse

user_router = APIRouter()


@user_router.get("/user/me", response_model=UserInformationResponse)
async def get_user(user=Depends(auth_service.get_current_user)):
    return user_service.get_user_info(user)


@user_router.post("/signup")
async def signup(sign_up: UserSignUp):
    user_service.signup_new(signup=sign_up)
    return JSONResponse(status_code=200, content="Sign up success")

@user_router.get("/test")
async def test(current_user=Depends(auth_service.get_current_user)):
    return participant_service.get_other_person_in_private_conversation(current_user=current_user)
