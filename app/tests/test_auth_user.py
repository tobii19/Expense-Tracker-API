from fastapi.testclient import TestClient
from main import app
from database.database import get_db, Base, engine
from models.user_auth import User_models
from sqlalchemy.orm import sessionmaker

client = TestClient(app)

def test_register_otp_flow():
    test_email = "testuser_otp@example.com"
    test_password = "securepassword123"
    test_name = "OTP Test User"

    # Clean up previous test run if exists
    client.delete(f"/auth/delete-users?email={test_email}")

    # 1. Register user
    reg_response = client.post(
        "/auth/register",
        json={"name": test_name, "email": test_email, "password": test_password},
    )
    assert reg_response.status_code == 200
    reg_data = reg_response.json()
    assert reg_data["is_verified"] is False
    assert reg_data["email"] == test_email

    # 2. Attempt login before OTP verification (should fail with 403)
    login_fail = client.post(
        "/auth/login",
        data={"username": test_email, "password": test_password},
    )
    assert login_fail.status_code == 403
    assert "not verified" in login_fail.json()["detail"].lower()

    # 3. Fetch OTP directly from database to test verification
    db_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    user_db = db_session.query(User_models).filter(User_models.email == test_email).first()
    assert user_db is not None
    assert user_db.otp is not None
    otp_code = user_db.otp
    db_session.close()

    # 4. Verify OTP with incorrect code (should fail with 400)
    verify_bad = client.post(
        "/auth/verify-otp",
        json={"email": test_email, "otp": "000000"},
    )
    assert verify_bad.status_code == 400

    # 5. Verify OTP with correct code
    verify_good = client.post(
        "/auth/verify-otp",
        json={"email": test_email, "otp": otp_code},
    )
    assert verify_good.status_code == 200
    verify_data = verify_good.json()
    assert "access_token" in verify_data
    assert verify_data["user"]["email"] == test_email

    # 6. Login after verification (should succeed with 200)
    login_success = client.post(
        "/auth/login",
        data={"username": test_email, "password": test_password},
    )
    assert login_success.status_code == 200
    assert "access_token" in login_success.json()

    # Cleanup after test
    client.delete(f"/auth/delete-users?email={test_email}")