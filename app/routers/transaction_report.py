from fastapi import APIRouter, Depends,HTTPException
from auth.oauth import get_current_user
from database.database import get_db
from models.transcation import Transaction
from schemas.transaction import TransactionType, Transaction_Response, SortBy, SortOrder
from models.user_auth import User_models
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func
from datetime import date
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/report", tags=["Report"])


@router.get("/spends")
def income_expense(
    db: Session = Depends(get_db), current_user: User_models = Depends(get_current_user)
):
    income = (
        db.query(func.sum(Transaction.amount))
        .filter(Transaction.user_id == current_user.id, Transaction.type == "income")
        .scalar()
        or 0
    )

    expense = (
        db.query(func.sum(Transaction.amount))
        .filter(Transaction.type == "expense", Transaction.user_id == current_user.id)
        .scalar()
        or 0
    )

    if not income or expense:
        logger.warning(
        "income or expense not found",
    )
    return {"Income": income, "Expense": expense}


@router.get("/monthly")
def monthly_report(
    month: int,
    year: int,
    type: Optional[TransactionType] = None,
    db: Session = Depends(get_db),
    current_user: User_models = Depends(get_current_user),
):
    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        func.extract("month", Transaction.date) == month,
        func.extract("year", Transaction.date) == year,
    )

    if type:
        query = query.filter(Transaction.type == type)

    total = query.with_entities(func.sum(Transaction.amount)).scalar() or 0

    transaction = query.all()

    return {
        "type": type,
        "total": total,
        "total transaction count": len(transaction),
        "transaction": transaction,
    }


@router.get("/sortby")
def sort_by(
    sort_by: Optional[SortBy] = None,
    sort_order: Optional[SortOrder] = SortOrder.desc,
    db: Session = Depends(get_db),
    current_user: User_models = Depends(get_current_user),
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    if sort_by == SortBy.date:
        if sort_order == SortOrder.asc:
            query = query.order_by(Transaction.date.asc())

        else:
            query = query.order_by(Transaction.date.desc())

    if sort_by == SortBy.amount:
        if sort_order == SortOrder.asc:
            query = query.order_by(Transaction.amount.asc())
        else:
            query = query.order_by(Transaction.amount.desc())

    transaction = query.all()

    return transaction


@router.get("/date_range")
def transaction_date_range(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    type: Optional[TransactionType] = None,
    current_user: User_models = Depends(get_current_user),
):
    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date,
    )
    if type:
        query = query.filter(Transaction.type == type)

    results = query.all()
    return results or []


@router.get("/amount_total")
def amount_minmax(
    start_date: date,
    end_date: date,
    type: Optional[TransactionType] = None,
    db: Session = Depends(get_db),
    current_user: User_models = Depends(get_current_user),
):
    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date,
    )
    
    if type:
        query = query.filter(Transaction.type == type)
        

    min_amount = query.with_entities(func.min(Transaction.amount)).scalar()
        
    max_amount = query.with_entities(func.max(Transaction.amount)).scalar()

    transaction = query.all()
    
    return {
        "min amount" : min_amount,
        "max amount" : max_amount,
        "start date " : start_date,
        "end date" : end_date,
        "transaction" : transaction
    }