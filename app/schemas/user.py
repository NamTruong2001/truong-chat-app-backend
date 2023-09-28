from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str


class UserInformationResponse(User):
    id: int


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserForJwtEncode(BaseModel):
    id: int
    username: str


class DecodedJwtUser(BaseModel):
    id: int
    username: str


class UserSignUp(User):
    password: str
