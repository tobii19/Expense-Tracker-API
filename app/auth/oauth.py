from jose import jwt, JWSError
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models.user_auth import User_models
from core.config import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email = payload.get("sub")

        if not email:
            raise HTTPException(status_code=400, detail="User Not Exists")

    except JWSError:
        raise HTTPException(status_code=400, detail="Invalid Token")

    user = db.query(User_models).filter(User_models.email == email).first()

    if not user:
        raise HTTPException(status_code=400, detail="User Not Exists")

    return user

    
