from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.app.api import auth, candidate, hr, websocket
from server.app.db import models, engine
from starlette.middleware.sessions import SessionMiddleware
import os
from server.app.services.redis_service import redis_pool

# 如果使用SQLAlchemy，运行创建表操作（生产环境中建议使用Alembic迁移）
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI面试平台")

#deepseek api_key=sk-a3639789c53545a98dfd9590c70f8d19

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
    expose_headers=["*"]    
)
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.urandom(32),
    session_cookie="session_cookie",
    max_age=3600,
    https_only=False,
    same_site="none")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(candidate.router, prefix="/candidate", tags=["Candidate"])
app.include_router(hr.router, prefix="/hr", tags=["HR"])
app.include_router(websocket.router, prefix="/websocket", tags=["websocket"])

@app.on_event("startup")
async def startup_event():
    # 测试连接
    if not redis_pool.ping():
        raise Exception("Failed to connect to Redis")

@app.on_event("shutdown")
async def shutdown_event():
    redis_pool.close()

@app.get("/")
def root():
    return {"message": "欢迎使用AI面试平台"}