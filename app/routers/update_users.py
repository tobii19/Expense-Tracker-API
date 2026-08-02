from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database.database import get_db
from models.user_auth import User_models
from schemas.users import CreateUser, UpdateUser, UserResponse, User
from auth.hashing import hashed_password, verify_password
from auth.oauth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from auth.jwt_handler import create_access_token

import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/update-user", tags=["Update User Account"])

def send_welcome_message(email: str):
    print(f"Your Account Updated : {email}")
    
@router.put("/profile", response_model=UserResponse)
@router.put("/register", response_model=UserResponse)
def update_user(user: UpdateUser, background_tasks: BackgroundTasks,db: Session = Depends(get_db),current_user : User_models = Depends(get_current_user)):
    exists = (
        db.query(User_models).filter(User_models.id == current_user.id).first()
    )

    if not exists:
        raise HTTPException(
                    status_code=409,
                    detail="User Not Exists",
                )

    exists.name = user.name
    exists.email = user.email
    if user.password:
        exists.password = hashed_password(user.password)

    db.commit()
    db.refresh(exists)

    background_tasks.add_task(
        send_welcome_message,
        exists.email,
    )
    
    return exists


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
    }
