from fastapi import APIRouter, HTTPException, Depends
from models.transcation import Transaction
from models.user_auth import User_models
from schemas.transcation import Transaction_Response, Create_Transcaion
from auth.oauth import get_current_user
from database.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/transaction", tags=["Transaction"])


@router.post("/")
def create_transaction(
    tran: Create_Transcaion,
    db: Session = Depends(get_db),
    current_user: User_models = Depends(get_current_user),
):
    entry = db.query(Transaction).filter(Transaction.user_id == current_user.id).first()

    new_tran = Transaction(
        name=tran.name,
        type=tran.type,
        description=tran.description,
        amount=tran.amount,
        user=current_user,
    )

    db.add(new_tran)
    db.commit()
    db.refresh(new_tran)

    return {
        "id": new_tran.id,
        "amount": new_tran.amount,
        "type": new_tran.type,
        "description": new_tran.description,
        "user": new_tran.user_id,
        "name": new_tran.name,
    }


@router.get("/")
def get_transaction(
    db: Session = Depends(get_db), current_user: User_models = Depends(get_current_user)
):
    tran = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    print(current_user.id)
    print(current_user.email)
    
    return tran
    

@router.get("/{name}", response_model=Transaction_Response)
def get_one(
    name: str,
    db: Session = Depends(get_db),
    current_user: User_models = Depends(get_current_user),
):
    tran = (
        db.query(Transaction)
        .filter(Transaction.name == name, Transaction.user_id == current_user.id)
        .first()
    )

    if not tran:
        raise HTTPException(status_code=404, detail="Not Found")

    return tran

