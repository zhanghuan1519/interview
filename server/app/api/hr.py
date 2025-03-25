from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from server.app.db import models, session_local
from pydantic import BaseModel
from server.app.services import deepseek_service

router = APIRouter()

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

# 创建岗位接口
class JobPostingCreate(BaseModel):
    job_title: str
    job_description: str
    requirements: str

@router.post("/job/create")
def create_job(posting: JobPostingCreate, hr_user_id: int, db: Session = Depends(get_db)):
    job = models.JobPosting(
        hr_user_id=hr_user_id,
        job_title=posting.job_title,
        job_description=posting.job_description,
        requirements=posting.requirements,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"message": "岗位创建成功", "job_posting_id": job.id}

# 设置面试规则
class InterviewConfigCreate(BaseModel):
    job_posting_id: int
    question_mode: str  # "AI", "manual", "mix"
    tech_percentage: float
    behavioral_percentage: float
    question_count: int
    answer_duration: int
    enable_follow_up: int

@router.post("/interview/config")
def set_interview_config(config: InterviewConfigCreate, db: Session = Depends(get_db)):
    new_config = models.InterviewConfig(
        job_posting_id=config.job_posting_id,
        question_mode=config.question_mode,
        tech_percentage=config.tech_percentage,
        behavioral_percentage=config.behavioral_percentage,
        question_count=config.question_count,
        answer_duration=config.answer_duration,
        enable_follow_up=config.enable_follow_up,
    )
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    return {"message": "面试规则设置成功", "interview_config_id": new_config.id}

# 其他HR模块接口，如简历筛选、发送面试邀请等，可按类似方式编写
class InterviewQuestionCreate(BaseModel):
    candidate_id: int

@router.post("/interview/create_question")
def create_question(interview : InterviewQuestionCreate, db: Session = Depends(get_db)):
    # 第二步: 获取候选人简历
    resume = db.query(models.Resume).filter(models.Resume.candidate_id == interview.candidate_id).order_by(models.Resume.uploaded_at.desc()).first()
    #resume = db.query(models.Resume).filter(models.Resume.id == interview.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    # 第三步: 获取岗位要求 
    sessions = db.query(models.InterviewSession).filter(models.InterviewSession.candidate_id == interview.candidate_id).order_by(models.InterviewSession.scheduled_time.desc()).first()
    if not sessions:
        raise HTTPException(status_code=404, detail="面试安排不存在")
    if sessions.status != "scheduled":
        return { "code": -1, "message": "候选人已经面试过或面试中出现违规，请联系HR"}
    job = db.query(models.JobPosting).filter(models.JobPosting.id == sessions.job_posting_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    config = db.query(models.InterviewConfig).filter(models.InterviewConfig.id == sessions.interview_config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="面试规则不存在")
    # 第四步: 通过deepseek创建面试问题
    # 首先构建deepseek请求
    try:
        result = deepseek_service.call_deepseek(
            question_count=config.question_count,
            tech_question_percent=config.tech_percentage,
            resume=resume.resume_txt,
            job_title=job.job_title,
            job_description=job.job_description,
            job_requirements=job.requirements
        )       
        # 第五步: 保存面试问题 
        try:
            order = 1
            for question in result["questions"]:
                new_question = models.InterviewSessionQuestion(
                    interview_session_id=sessions.id,
                    question_text=question["content"],
                    question_type=question["type"],
                    order_number=order,
                    answer_time_limit=40,
                    is_auto_generated=1
                )
                order = order + 1
                db.add(new_question)
            db.commit()
            
            result = db.query(models.)
        except Exception as ex:
            db.rollback()
            raise HTTPException(status_code=500, detail="保存面试问题到数据库时发生错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deepseek服务异常：{e}")    
    
    return {"code": 0, "message": "面试问题创建成功", "questions": result["questions"]}