import aiofiles
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Path
from server.app.db import models
from sqlalchemy.orm import Session
from server.app.db import session_local
from pydantic import BaseModel
from sqlalchemy import and_
from datetime import datetime, timezone
from server.app.core import security
from server.app.services.redis_service import redis_pool
from fastapi.params import Query
import os

router = APIRouter()

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

# 示例：面试者登录（手机验证码登录示例）
class CandidateLogin(BaseModel):
    contact: str
    type: str  # "phone" or "email"
    code: str  # 验证码

@router.get("/test")
def test():
    return {"message": "Hello, World test!"}

@router.post("/logout")
def candidate_logout(candidate_id: int = Query(...)):
    if redis_pool.exists("candidate_" + str(candidate_id)):
        redis_pool.delete("candidate_" + str(candidate_id))
    return {"message": "登出成功", "code": 0}

@router.post("/login")
def candidate_login(data: CandidateLogin, request: Request, db: Session = Depends(get_db)):
    if data.type == "phone":
        candidate = db.query(models.CandidateUser).filter(models.CandidateUser.phone == data.contact).first()
    else:
        candidate = db.query(models.CandidateUser).filter(models.CandidateUser.email == data.contact).first()
    if not candidate:
        return {"message": "用户不存在", "code": -1}
    
    now_time = datetime.utcnow()
    now_time_str = now_time.strftime("%Y-%m-%d %H:%M:%S")
    if data.type == "phone":
        code = db.query(models.VerificationCode).filter(and_(
            models.VerificationCode.phone == data.contact, 
            models.VerificationCode.code == data.code,
            models.VerificationCode.expires_at >= now_time_str
            )).first()
    else:
        code = db.query(models.VerificationCode).filter(and_(
            models.VerificationCode.email == data.contact, 
            models.VerificationCode.code == data.code,
            models.VerificationCode.expires_at >= now_time_str
            )).first()
    if not code:
        return {"message": "无效的验证码", "code": -2}
    
    isession = db.query(models.InterviewSession).filter(
        models.InterviewSession.candidate_id==candidate.id
        ).order_by(models.InterviewSession.scheduled_time.desc()).first()
    if not isession:
        return {"message": "面试不存在", "code": -1}
    if isession.status != 'scheduled':
        return {"message": "面试不存在或已经完成该轮面试", "code": -3}
    
    # 此处应验证短信验证码，示例直接返回成功
    if redis_pool.exists("candidate_" + str(candidate.id)):
        redis_pool.delete("candidate_" + str(candidate.id))
    redis_pool.set("candidate_" + str(candidate.id), str(candidate.id), ex=60*60*24)

    return {"message": "登录成功", "candidate_id": candidate.id, "code": 0 }

# 个人信息确认
class CandidateInfo(BaseModel):
    name: str
    email: str

@router.post("/confirm")
def confirm_info(info: CandidateInfo, candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(models.CandidateUser).filter(models.CandidateUser.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="用户不存在")
    candidate.name = info.name
    candidate.email = info.email
    db.commit()
    return {"message": "信息确认成功"}

# 其他接口（拍照存档、设备检测、AI面试、查看结果）可以依此模式添加


@router.post("/is_login")
async def is_login(request: Request):
    body = await request.json()
    candidate_id = body.get('candidate_id')
    if not redis_pool.exists("candidate_" + str(candidate_id)):
        return {"message": "未登录", "code": -1}
    return {"message": "已经登录", "code": 0}

async def get_current_user(request: Request):
    body = await request.json()
    candidate_id = body.get('candidate_id')
    if not redis_pool.exists("candidate_" + str(candidate_id)):
        print("未登录")
        raise HTTPException(status_code=401, detail="未登录")
    return candidate_id

@router.post("/profile", dependencies=[Depends(get_current_user)])
async def get_profile(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    candidate_id = body.get('candidate_id')
    candidate = db.query(models.CandidateUser).filter(models.CandidateUser.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="用户不在候选人名单中")
    resume = db.query(models.Resume).filter(models.Resume.candidate_id == candidate_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="用户简历不存在")
    return resume


class ResumeBasicInfo(BaseModel):
    parsed_name: str
    birth: str
    phone: str
    gender: str
    degree: str
    email: str
    candidate_id: str

@router.post("/save_resume_basic_info", dependencies=[Depends(get_current_user)])
async def save_resume(info: ResumeBasicInfo, request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    candidate_id = body.get('candidate_id')
    resume = db.query(models.Resume).filter(models.Resume.candidate_id == candidate_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="用户简历不存在")
    resume.parsed_name = info.parsed_name
    resume.birthdate = info.birth
    resume.phone = info.phone
    resume.gender = info.gender
    resume.degree = info.degree
    resume.email = info.email
    try:
        db.commit()
    except Exception as e:
        return {"message": "简历保存失败", "code": -1}
    return {"message": "简历保存成功", "code": 0}

@router.get("/position_info/{candidate_id}")
async def get_position_info(candidate_id: int, request: Request, db: Session = Depends(get_db)):
    interview_session = db.query(models.InterviewSession).filter(models.InterviewSession.candidate_id==candidate_id).order_by(models.InterviewSession.scheduled_time.desc()).first()
    if not interview_session:
        raise HTTPException(status_code=404, detail="面试安排不存在")
    job = db.query(models.JobPosting).filter(models.JobPosting.id == interview_session.job_posting_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位信息不存在")
    return { "message": "获取岗位信息成功", "code": 0, "job": job }


class InterviewStatus(BaseModel):
    candidate_id: int
    status: str
    
@router.post("/interview_status")
async def update_interview_status(interviewStatus: InterviewStatus, request: Request, db: Session = Depends(get_db)):
    status = db.query(models.InterviewSession).filter(
        models.InterviewSession.candidate_id==interviewStatus.candidate_id, models.InterviewSession.status=="scheduled"
        ).order_by(models.InterviewSession.scheduled_time.desc()).first()
    if not status:
        raise HTTPException(status_code=404, detail="面试安排不存在")
    utc_time = datetime.now(timezone.utc)
    status.status = interviewStatus.status
    status.actual_start_time = utc_time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        db.commit()
    except Exception as e:
        return {"message": "面试状态保存失败", "code": -1}
    return {"message": "面试状态保存成功", "code": 0}


UPLOAD_DIR = "audio"

@router.post("/upload_audio/{candidate_id}")
async def upload_audio(candidate_id: int = Path(..., title="候选人ID", gt=0), file: UploadFile = File(...)):
    try:
        
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        # 生成安全文件名
        timestamp = datetime.now().strftime(f"{candidate_id}_%Y%m%d_%H%M%S")
        file_ext = os.path.splitext(file.filename)[1]
        safe_filename = f"audio_{timestamp}{file_ext}"
        
        # 保存文件
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        async with aiofiles.open(file_path, "wb") as f:
            while True:
                # 分块读取（避免内存溢出）
                chunk = await file.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                await f.write(chunk)        
        return {"message": "success", "file_path": "", "code": 0}
    except Exception as e:
        return {"message": str(e), "code": -1}
