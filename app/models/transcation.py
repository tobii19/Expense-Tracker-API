from sqlalchemy import Column, String, Integer, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import date


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, default=date.today)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    user = relationship(
        "User_models",
        back_populates="transactions",
    )