from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_job():
    # 此处hr_user_id需提前创建用户
    response = client.post("/hr/job/create", json={
        "job_title": "软件工程师",
        "job_description": "负责开发AI面试系统",
        "requirements": "本科及以上学历"
    }, params={"hr_user_id": 1})
    assert response.status_code == 200
