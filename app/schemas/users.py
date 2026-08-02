from pydantic import BaseModel, EmailStr, ConfigDict


# -----------------------------
# Register User
# -----------------------------
from pydantic import BaseModel, Field

class CreateUser(BaseModel):
    name: str
    email: str
    password: str = Field(min_length=8, max_length=72)


# -----------------------------
# Update User
# -----------------------------
class UpdateUser(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class User(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str

class ResendOTP(BaseModel):
    email: EmailStr

class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    email: EmailStr
    otp: str
    new_password: str