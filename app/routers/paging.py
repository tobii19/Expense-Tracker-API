from fastapi import APIRouter, HTTPException, Depends
from models.transcation import Transaction
from sqlalchemy.orm import Session
from models.user_auth import User_models
from schemas.transaction import (
    Transaction_Response,
    TransactionType,
    Create_Transaction,
)
from auth.oauth import get_current_user
from database.database import get_db
from typing import List, Optional
from sqlalchemy import or_
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pagination", tags=["Pagination"])


@router.get("/", response_model=List[Transaction_Response])
def pagination(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User_models = Depends(get_current_user),
):
    offset = max(0, (page - 1) * page_size)

    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return transactions or []


@router.get("/search")
def search(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User_models = Depends(get_current_user),
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if search:
        query = query.filter(
            or_(
                Transaction.name.ilike(f"%{search}%"),
                Transaction.description.ilike(f"%{search}%"),
            )
        )
    transactions = query.all()
    
    return transactions or []