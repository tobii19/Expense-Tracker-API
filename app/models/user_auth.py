from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base


class User_models(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)

    transactions = relationship(
        "Transaction", back_populates="user", cascade="all, delete-orphan"
    )
