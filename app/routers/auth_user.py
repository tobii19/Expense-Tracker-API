from services.email import send_otp_email, send_forgot_password_otp_email

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from database.database import get_db
from models.user_auth import User_models
from schemas.users import (
    CreateUser,
    UpdateUser,
    UserResponse,
    User,
    VerifyOTP,
    ResendOTP,
    ForgotPassword,
    ResetPassword,
)
from auth.hashing import hashed_password, verify_password
from auth.oauth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from auth.jwt_handler import create_access_token
from models.transcation import Transaction
import logging

from services.otp import otp_generate_otp
from datetime import timedelta, datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
def register(
    user: CreateUser, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User_models).filter(User_models.email == user.email).first()
    )

    if existing_user:
        if existing_user.is_verified:
            logger.warning(
                "Registration failed. Email '%s' already exists and is verified.",
                user.email,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User Already Exists. Please log in.",
            )
        else:
            # User exists but is not verified: update details and send a new OTP
            existing_user.name = user.name
            existing_user.password = hashed_password(user.password)
            otp = otp_generate_otp()
            existing_user.otp = otp
            existing_user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)
            db.commit()
            db.refresh(existing_user)

            background_tasks.add_task(send_otp_email, existing_user.email, otp)
            return {
                "message": "User exists but was unverified. A new verification OTP has been sent to your email.",
                "email": existing_user.email,
                "is_verified": False,
            }

    # Create new user
    register_user = User_models(
        name=user.name,
        email=user.email,
        password=hashed_password(user.password),
        is_verified=False,
    )

    otp = otp_generate_otp()
    register_user.otp = otp
    register_user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)

    db.add(register_user)
    db.commit()
    db.refresh(register_user)

    background_tasks.add_task(send_otp_email, register_user.email, otp)

    return {
        "message": "Registration successful! Verification OTP sent to your email.",
        "email": register_user.email,
        "is_verified": False,
    }


@router.post("/verify-otp")
def verify_otp(data: VerifyOTP, db: Session = Depends(get_db)):
    user = db.query(User_models).filter(User_models.email == data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user.is_verified:
        token = create_access_token({"sub": user.email})
        return {
            "message": "Account is already verified.",
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": user.id, "name": user.name, "email": user.email},
        }

    if not user.otp or user.otp != data.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP code"
        )

    if not user.otp_expiry or datetime.utcnow() > user.otp_expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new OTP.",
        )

    user.is_verified = True
    user.otp = None
    user.otp_expiry = None
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.email})

    return {
        "message": "Email verified successfully!",
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "name": user.name, "email": user.email},
    }


@router.post("/resend-otp")
def resend_otp(
    data: ResendOTP, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    user = db.query(User_models).filter(User_models.email == data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user.is_verified:
        return {"message": "Account is already verified. You can log in."}

    otp = otp_generate_otp()
    user.otp = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)
    db.commit()

    background_tasks.add_task(send_otp_email, user.email, otp)

    return {"message": "A new OTP has been sent to your email address."}


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    exists = (
        db.query(User_models).filter(User_models.email == form_data.username).first()
    )

    if not exists:
        logger.warning("Email does not exist '%s'", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User Not Exists"
        )

    if not verify_password(form_data.password, exists.password):
        logger.warning("Invalid Password for '%s'", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Password"
        )

    if not exists.is_verified:
        logger.warning("User '%s' attempted login without email verification", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your OTP to access your account.",
        )

    token = create_access_token({"sub": exists.email})

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/forgot-password")
def forgot_password(
    data: ForgotPassword,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(User_models).filter(User_models.email == data.email).first()

    if user:
        otp = otp_generate_otp()
        user.otp = otp
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        db.commit()

        background_tasks.add_task(send_forgot_password_otp_email, user.email, otp)

    return {
        "message": "If an account with that email exists, a password reset OTP has been sent to your email."
    }


@router.post("/reset-password")
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    user = db.query(User_models).filter(User_models.email == data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not user.otp or user.otp != data.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP code"
        )

    if not user.otp_expiry or datetime.utcnow() > user.otp_expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new password reset OTP.",
        )

    user.password = hashed_password(data.new_password)
    user.otp = None
    user.otp_expiry = None
    db.commit()

    return {
        "message": "Password reset successfully. You can now log in with your new password."
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
    }


@router.delete("/delete-users")
def delete_user(email: str, db: Session = Depends(get_db)):
    user = db.query(User_models).filter(User_models.email == email).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    transactions = db.query(Transaction).filter(Transaction.user_id == user.id).all()

    for transaction in transactions:
        db.delete(transaction)

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
