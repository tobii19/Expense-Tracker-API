from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert "Expense Tracker" in response.text or response.json() == {"message": "Expense Tracker API Running"}
    
