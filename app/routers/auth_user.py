from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from models.user_auth import User_models
from schemas.users import CreateUser, UpdateUser, UserResponse, User
from auth.hashing import hashed_password, verify_password
from auth.oauth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register(user: CreateUser, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User_models).filter(User_models.email == user.email).first()
    )

    if existing_user:
        raise HTTPException(status_code=409, detail="User Already Exists")

    register_user = User_models(
        name=user.name, email=user.email, password=hashed_password(user.password)
    )

    db.add(register_user)
    db.commit()
    db.refresh(register_user)

    return register_user


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    exists = (
        db.query(User_models).filter(User_models.email == form_data.username).first()
    )

    if not exists:
        raise HTTPException(status_code=404, detail="User Not Exists")

    if not verify_password(form_data.password, exists.password):
        raise HTTPException(status_code=404, detail="Invalid Password")

    token = create_access_token({"sub": exists.email})
    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
    }
