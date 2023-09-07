from datetime import datetime
from schemas import UserSignUp
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from model import UserModel

async def signup_new(signup: UserSignUp, db: Session):
    if db.query(UserModel).filter(UserModel.email == signup.email).first():
        raise HTTPException(status_code=400, detail="Email already exist!")
    
    if db.query(UserModel).filter(UserModel.username == signup.username).first():
        raise HTTPException(status_code=400, detail="Username already exist!")
    
    new_user = UserModel(**signup.model_dump(), 
                         created_at=datetime.now(), 
                         updated_at=datetime.now(),
                         is_active=False)
    db.add(new_user)
    db.commit()
    