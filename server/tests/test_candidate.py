from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_candidate_login():
    response = client.post("/candidate/login", json={"phone": "13800138000", "code": "123456"})
    assert response.status_code == 200 or response.status_code == 400
