from fastapi import APIRouter, HTTPException, Depends
from models.transcation import Transaction
from sqlalchemy.orm import Session
from models.user_auth import User_models
from auth.oauth import get_current_user
from database.database import get_db
from sqlalchemy import or_
from sqlalchemy import func

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/")
def dashboard(db : Session = Depends(get_db),current_user : User_models = Depends(get_current_user)):
    income = db.query(func.sum(Transaction.amount)).filter(Transaction.user_id == current_user.id, Transaction.type == "income").scalar() or 0
    expense = db.query(func.sum(Transaction.amount)).filter(Transaction.user_id == current_user.id, Transaction.type == "expense").scalar() or 0
    
    count = db.query(func.count(Transaction.id)).filter(Transaction.user_id == current_user.id).scalar() or 0
    expense_max = db.query(func.max(Transaction.amount)).filter(Transaction.user_id == current_user.id, Transaction.type == "expense").scalar() or 0
    expense_min = db.query(func.min(Transaction.amount)).filter(Transaction.user_id == current_user.id, Transaction.type == "expense").scalar() or 0
    
    income_max = db.query(func.max(Transaction.amount)).filter(Transaction.user_id == current_user.id, Transaction.type == "income").scalar() or 0
    income_min = db.query(func.min(Transaction.amount)).filter(Transaction.user_id == current_user.id, Transaction.type == "income").scalar() or 0
        
    last = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.date.desc())
        .first()
    )    

    return {
        "income": income,
        "expense": expense,
        "balance": income - expense,
        "total transaction": count,
        "highest_income": income_max,
        "highest_expense": expense_max,
        "lowest_income": income_min,
        "lowest_expense": expense_min,
        "last transaction": last
    }

    