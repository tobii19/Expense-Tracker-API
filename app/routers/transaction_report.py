from fastapi import APIRouter,HTTPException,Depends
from auth.oauth import get_current_user
from database.database import get_db
from models.transcation import Transaction
from schemas.transcation import Transaction_Response
from models.user_auth import User_models
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
router = APIRouter(
    prefix="/report",
    tags=["Report"]
)

@router.get("/monthly")
def income_expense(db : Session = Depends(get_db),current_user : User_models = Depends(get_current_user)):
    income = (db.query(func.sum(Transaction.amount)).filter(Transaction.user_id == current_user.id,Transaction.type == "income").scalar() or 0)

    
    expense = (db.query(func.sum(Transaction.amount)).filter(Transaction.type == "expense",Transaction.user_id == current_user.id).scalar() or 0)
    
    return {
            "Income":income,
            "Expense":expense
        }

def a():
    pass