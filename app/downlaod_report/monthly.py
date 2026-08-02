from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from auth.oauth import get_current_user
from schemas.transaction import Transaction_Response,TransactionType
from models.transcation import Transaction
from models.user_auth import User_models
from datetime import date
from sqlalchemy import func

from io import BytesIO
from openpyxl import Workbook
from fastapi.responses import StreamingResponse



router = APIRouter(
    prefix="/report-downlaod",
    tags=["Report Download"]
)

@router.get("/export-monthly",response_class=StreamingResponse)
def export_monthly(start_date : date,end_date : date, db : Session = Depends(get_db),current_user : User_models = Depends(get_current_user)):
    transaction = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date
        ).all()

    if not transaction:
        raise HTTPException(status_code=404,detail="Transaction not found or Enter Proper Date")

    workbook = Workbook() 
    
    sheet = workbook.active
    
    sheet.title = "Transaction"
    
    sheet.append([
        "ID",
        "Name",
        "Description",
        "Amount",
        "Type",
        "Date",
        "User ID"
    ])
    
    for tran in transaction:

        sheet.append([
            tran.id,
            tran.name,
            tran.description,
            tran.amount,
            tran.type,
            tran.date,
            tran.user_id
        ])
            
    excel = BytesIO()
    
    workbook.save(excel)
    
    excel.seek(0)
    
    return StreamingResponse(
        excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=transaction.xlsx"
        }
    )