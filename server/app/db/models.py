from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, Enum, Float, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func, text
from datetime import datetime, timedelta
import enum

Base = declarative_base()

# 企业信息表
class Enterprise(Base):
    __tablename__ = "enterprise"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), comment="企业名称")
    verification_status = Column(SmallInteger, default=0, comment="企业认证状态：0-未认证，1-已认证")
    license = Column(Text, comment="营业执照上传图片地址")
    code = Column(String(4), comment="4位企业码")

# HR用户表
class HRUser(Base):
    __tablename__ = "hr_users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="用户名称")
    email = Column(String(255), unique=True, comment="HR登录邮箱")
    phone = Column(String(20), unique=True, comment="HR手机号码")
    password_hash = Column(String(255), nullable=False, comment="密码哈希值")
    enterprise_id = Column(Integer, ForeignKey("enterprise.id", ondelete="CASCADE"), comment="关联企业信息表")
    role = Column(Enum("admin", "manager", "member", name="role_enum"), default="member", comment="系统角色")
    team_name = Column(String(255), comment="团队名称")
    created_at = Column(DateTime, server_default=func.now(), comment="账户创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="最后更新时间")

# 候选人用户表
class CandidateUser(Base):
    __tablename__ = "candidate_users"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, nullable=False, comment="候选人手机号码")
    name = Column(String(255), comment="候选人姓名")
    email = Column(String(255), comment="候选人邮箱")
    identity_photo_path = Column(String(255), comment="面试前拍摄照片存储路径")
    created_at = Column(DateTime, server_default=func.now(), comment="记录创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="最后更新时间")

# 简历表
class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_users.id", ondelete="CASCADE"), comment="关联候选人ID")
    gender = Column(Enum("male", "female", name="gender_enum"), comment="候选人性别")
    birth = Column(String(10), comment="候选人生日")
    degree = Column(String(255), comment="候选人学历")
    phone = Column(String(45), comment="候选人手机号码")
    email = Column(String(100), comment="候选人邮箱")
    file_path = Column(String(255), nullable=False, comment="上传的简历文件存储路径")
    parsed_name = Column(String(255), comment="解析出的姓名")
    resume_txt = Column(Text, comment="简历文本内容")
    uploaded_at = Column(DateTime, server_default=func.now(), comment="简历上传时间")

# 岗位发布表
class JobPosting(Base):
    __tablename__ = "job_postings"
    id = Column(Integer, primary_key=True, index=True)
    hr_user_id = Column(Integer, ForeignKey("hr_users.id", ondelete="CASCADE"), comment="发布岗位的HR用户ID")
    job_title = Column(String(255), nullable=False, comment="岗位名称")
    job_description = Column(Text, comment="岗位描述")
    requirements = Column(Text, comment="岗位要求")
    created_at = Column(DateTime, server_default=func.now(), comment="岗位发布时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="最后更新时间")

# 面试规则配置表
class InterviewConfig(Base):
    __tablename__ = "interview_configs"
    id = Column(Integer, primary_key=True, index=True)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id", ondelete="CASCADE"), comment="关联的岗位ID")
    question_mode = Column(Enum("AI", "manual", "mix", name="question_mode_enum"), default="mix", comment="问题生成模式")
    tech_percentage = Column(DECIMAL(5,2), default=80.00, comment="技术类问题占比")
    behavioral_percentage = Column(DECIMAL(5,2), default=20.00, comment="行为类问题占比")
    question_count = Column(Integer, default=10, comment="每场面试题目数量")
    answer_duration = Column(Integer, default=300, comment="每题最大答题时长（秒）")
    enable_follow_up = Column(SmallInteger, default=0, comment="是否启用追问逻辑")
    created_at = Column(DateTime, server_default=func.now(), comment="配置创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="最后更新时间")

# 面试会话表
class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidate_users.id", ondelete="CASCADE"), comment="关联候选人ID")
    job_posting_id = Column(Integer, ForeignKey("job_postings.id", ondelete="CASCADE"), comment="关联岗位ID")
    interview_config_id = Column(Integer, ForeignKey("interview_configs.id", ondelete="CASCADE"), comment="使用的面试配置ID")
    scheduled_time = Column(DateTime, comment="预定面试时间")
    actual_start_time = Column(DateTime, comment="实际面试开始时间")
    actual_end_time = Column(DateTime, comment="实际面试结束时间")
    session_link = Column(String(255), comment="面试会话链接")
    status = Column(Enum("scheduled", "ongoing", "completed", "cancelled", "no_show", name="session_status_enum"), default="scheduled", comment="面试状态")
    created_at = Column(DateTime, server_default=func.now(), comment="会话创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="最后更新时间")

# 面试会话题目表
class InterviewSessionQuestion(Base):
    __tablename__ = "interview_session_questions"
    id = Column(Integer, primary_key=True, index=True)
    interview_session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), comment="关联的面试会话ID")
    question_text = Column(Text, nullable=False, comment="题目文本")
    question_type = Column(Enum("technical", "behavioral", "other", name="question_type_enum"), default="technical", comment="题目类型")
    is_auto_generated = Column(SmallInteger, default=1, comment="是否由AI自动生成")
    order_number = Column(Integer, comment="题目顺序号")
    answer_time_limit = Column(Integer, comment="答题时长限制（秒）")
    created_at = Column(DateTime, server_default=func.now(), comment="题目生成时间")

# 面试回答表
class InterviewAnswer(Base):
    __tablename__ = "interview_answers"
    id = Column(Integer, primary_key=True, index=True)
    session_question_id = Column(Integer, ForeignKey("interview_session_questions.id", ondelete="CASCADE"), comment="关联的面试题目ID")
    answer_text = Column(Text, comment="候选人文字回答内容")
    answer_video_path = Column(Text, comment="候选人回答视频文件存储路径")
    answer_audio_path = Column(Text, comment="候选人回答音频文件存储路径")
    answer_start_time = Column(DateTime, comment="回答开始时间")
    answer_end_time = Column(DateTime, comment="回答结束时间")
    created_at = Column(DateTime, server_default=func.now(), comment="回答记录生成时间")

# 面试监控日志表
class InterviewMonitoringLog(Base):
    __tablename__ = "interview_monitoring_logs"
    id = Column(Integer, primary_key=True, index=True)
    interview_session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), comment="关联的面试会话ID")
    log_type = Column(String(50), comment="日志类型")
    description = Column(Text, comment="详细描述信息")
    log_timestamp = Column(DateTime, server_default=func.now(), comment="日志记录时间")

# 面试结果表
class InterviewResult(Base):
    __tablename__ = "interview_results"
    id = Column(Integer, primary_key=True, index=True)
    interview_session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), comment="关联的面试会话ID")
    score_language = Column(String(10), comment="语言表达评分")
    score_logic = Column(String(10), comment="逻辑思维评分")
    score_skill = Column(String(10), comment="技能匹配度评分")
    overall_score = Column(DECIMAL(5,2), comment="综合评分")
    result = Column(Text, comment="详细评分报告")
    created_at = Column(DateTime, server_default=func.now(), comment="结果生成时间")

# 订阅套餐表
class SubscriptionPackage(Base):
    __tablename__ = "subscription_packages"
    id = Column(Integer, primary_key=True, index=True)
    package_name = Column(String(255), nullable=False, comment="套餐名称")
    price = Column(DECIMAL(10,2), nullable=False, comment="套餐价格")
    interview_session_limit = Column(Integer, comment="面试场次上限")
    candidate_limit = Column(Integer, comment="候选人数量上限")
    description = Column(Text, comment="套餐详细描述")
    created_at = Column(DateTime, server_default=func.now(), comment="套餐创建时间")

# HR订阅记录表
class HRSubscription(Base):
    __tablename__ = "hr_subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    hr_user_id = Column(Integer, ForeignKey("hr_users.id", ondelete="CASCADE"), comment="关联的HR用户ID")
    package_id = Column(Integer, ForeignKey("subscription_packages.id", ondelete="CASCADE"), comment="关联的套餐ID")
    purchase_date = Column(DateTime, server_default=func.now(), comment="购买时间")
    expiry_date = Column(DateTime, comment="套餐到期时间")
    status = Column(Enum("active", "expired", "cancelled", name="subscription_status_enum"), default="active", comment="套餐状态")

# 自动邮件日志表
class EmailLog(Base):
    __tablename__ = "email_logs"
    id = Column(Integer, primary_key=True, index=True)
    hr_user_id = Column(Integer, ForeignKey("hr_users.id", ondelete="SET NULL"), nullable=True)
    candidate_id = Column(Integer, ForeignKey("candidate_users.id", ondelete="SET NULL"), nullable=True)
    email_address = Column(String(255), nullable=False, comment="接收邮件邮箱")
    subject = Column(String(255), nullable=False, comment="邮件主题")
    content = Column(Text, comment="邮件内容")
    sent_at = Column(DateTime, server_default=func.now(), comment="邮件发送时间")
    status = Column(Enum("sent", "failed", name="email_status_enum"), default="sent", comment="发送状态")

# 登录日志表
class LoginLog(Base):
    __tablename__ = "login_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_type = Column(Enum("hr", "candidate", name="user_type_enum"), nullable=False, comment="用户类型")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    login_time = Column(DateTime, server_default=func.now(), comment="登录时间")
    ip_address = Column(String(50), comment="登录IP")
    device_info = Column(String(255), comment="设备信息")
    status = Column(Enum("success", "failure", name="login_status_enum"), default="success", comment="登录状态")

# 短信验证码表
class VerificationCode(Base):
    __tablename__ = "verification_codes"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    code = Column(String(6), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, server_default=func.now() + text("INTERVAL '1 MINUTE'"))
