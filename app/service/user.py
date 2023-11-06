from datetime import datetime

from fastapi.exceptions import HTTPException

from db import MysqlDBAdapter
from model import UserModel
from schemas import UserSignUp, UserInformationResponse


class UserService:
    def __init__(self, db_adapter: MysqlDBAdapter):
        self.db_adapter = db_adapter

    def signup_new(self, signup: UserSignUp):
        with self.db_adapter.get_session() as session:
            if session.query(UserModel).filter(UserModel.email == signup.email).first():
                raise HTTPException(status_code=400, detail="Email already exist!")

            if session.query(UserModel).filter(UserModel.username == signup.username).first():
                raise HTTPException(status_code=400, detail="Username already exist!")

            new_user = UserModel(**signup.model_dump(),
                                 created_at=datetime.now(),
                                 updated_at=datetime.now(),
                                 )
            session.add(new_user)
            session.commit()

    def get_user_info(self, user_model: UserModel) -> UserInformationResponse:
        return UserInformationResponse(id=user_model.id,
                                       email=user_model.email,
                                       first_name=user_model.first_name,
                                       last_name=user_model.last_name,
                                       username=user_model.username)
