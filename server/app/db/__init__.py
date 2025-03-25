from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.app.core.config import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 导入所有模型，确保创建表时能够找到
from server.app.db import models
