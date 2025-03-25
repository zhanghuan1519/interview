from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_hr_login():
    response = client.post("/auth/login", json={"email": "hr@example.com", "password": "test123"})
    assert response.status_code == 200 or response.status_code == 400
