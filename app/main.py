from fastapi import FastAPI
from routers.auth_user import router as auth_user_router
from routers.transcation import router as Transaction_router
from database.database import engine,Base
from routers.transaction_report import router as report_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API")

app.include_router(auth_user_router)
app.include_router(Transaction_router)
app.include_router(report_router)

@app.get("/")
def root():
    return {
        "message":"Expense Tracker API Running"
    }