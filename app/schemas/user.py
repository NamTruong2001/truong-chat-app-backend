from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str


class UserLoginResponse(BaseModel):
    id: int
    username: str


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserForJwtEncode(BaseModel):
    id: int
    username: str
