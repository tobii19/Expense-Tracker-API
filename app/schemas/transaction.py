from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date
from typing import Optional
from enum import Enum


class Create_Transaction(BaseModel):
    name: str
    type: str
    description: Optional[str] = ""
    date: Optional[date] = None
    amount: float
    customer_type: Optional[str] = "standard"


class Transaction_Response(BaseModel):
    id: int
    name: str
    amount: float
    type: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class SortBy(str, Enum):
    date = "date"
    amount = "amount"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"