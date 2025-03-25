from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from server.app.core import security
from server.app.db import models, schemas
from sqlalchemy.orm import Session
from server.app.db import session_local
import random
import string
from datetime import datetime, timedelta
from server.app.services import sms_service
from server.app.services import email_service

router = APIRouter()

# 示例用户登录模型
class Token(BaseModel):
    access_token: str
    token_type: str

class AuthDetails(BaseModel):
    contact: str
    code: str
    type: str  # "phone" or "email"

class VerificationRequest(BaseModel):
    contact: str
    type: str  # "phone" or "email"

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=Token)
def login(auth_details: AuthDetails, db: Session = Depends(get_db)):
    # 示例：根据邮箱查询用户
    if auth_details.type == "phone":
        user = db.query(models.HRUser).filter(models.HRUser.phone == auth_details.contact).first()
    else:
        user = db.query(models.HRUser).filter(models.HRUser.email == auth_details.contact).first()
    if not user:
        raise HTTPException(status_code=400, detail="无效的邮箱或密码")
    if not security.verify_password(auth_details.password, user.password_hash):
        raise HTTPException(status_code=400, detail="无效的邮箱或密码")
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/generate-code")
def generate_code(request: VerificationRequest, db: Session = Depends(get_db)):
    # 生成6位数字验证码
    code = ''.join(random.choices(string.digits, k=6))
    created_at = datetime.utcnow()
    expires_at = created_at + timedelta(minutes=1)

    # 格式化日期时间为 "YYYY-MM-DD HH:MM:SS"
    created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
    expires_at_str = expires_at.strftime("%Y-%m-%d %H:%M:%S")

    # 存储到verification_codes表
    if request.type == "phone":
        verification_code = models.VerificationCode(phone=request.contact, code=code, expires_at=expires_at_str, created_at=created_at_str) 
    else:
        verification_code = models.VerificationCode(email=request.contact, code=code, expires_at=expires_at_str, created_at=created_at_str)
    db.add(verification_code)
    db.commit()

    if request.type == "phone":
        # 实际中调用短信服务接口
        sms_service.send_sms(request.contact, code)
    elif request.type == "email":
        # 实际中调用邮件服务接口
        email_service.send_email(request.contact, code)
    else:  # 不支持的验证方式
        raise HTTPException(status_code=400, detail="不支持的验证方式")
    return {"message": "验证码已发送"}