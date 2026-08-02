from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import relationship
from database.database import Base


class User_models(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True,)
    name = Column(String,nullable=False,index=True,)
    email = Column(String,unique=True,nullable=False,index=True,)
    password = Column(String,nullable=False,)
    is_verified = Column(Boolean,default=False,)
    otp = Column(String,nullable=True,)
    otp_expiry = Column(DateTime,nullable=True,)
    transactions = relationship("Transaction",back_populates="user",cascade="all, delete-orphan",)
