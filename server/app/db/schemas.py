from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class HRUserSchema(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    enterprise_id: int

    class Config:
        orm_mode = True

class CandidateUserSchema(BaseModel):
    id: int
    phone: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    identity_photo_path: Optional[str] = None

    class Config:
        orm_mode = True

class VerificationCodeSchema(BaseModel):
    id: int
    phone: Optional[str] = None
    email: Optional[str] = None
    code: str
    type: str
    expires_at: datetime
    created_at: datetime

    class Config:
        orm_mode = True

# 其他Schema按照需求定义，如JobPostingSchema、InterviewConfigSchema等
