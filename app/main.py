from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from routers.auth_user import router as auth_user_router
from routers.transcation import router as Transaction_router
from database.database import engine, Base
from routers.transaction_report import router as report_router
from routers.paging import router as page_router
from routers.dashboard import router as dashboard_router
from routers.update_users import router as update_router
from downlaod_report.monthly import router as downlaod_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_user_router)
app.include_router(Transaction_router)
app.include_router(report_router)
app.include_router(page_router)
app.include_router(dashboard_router)
app.include_router(update_router)
app.include_router(downlaod_router)

frontend_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "frontend",
)

if os.path.exists(frontend_path):
    css_path = os.path.join(frontend_path, "css")
    js_path = os.path.join(frontend_path, "js")

    if os.path.exists(css_path):
        app.mount("/css", StaticFiles(directory=css_path), name="css")

    if os.path.exists(js_path):
        app.mount("/js", StaticFiles(directory=js_path), name="js")

    app.mount(
        "/frontend",
        StaticFiles(directory=frontend_path, html=True),
        name="frontend",
    )


@app.get("/")
def root():
    index_file = os.path.join(frontend_path, "index.html")

    if os.path.exists(index_file):
        return FileResponse(index_file)

    return {
        "message": "Expense Tracker API Running"
    }