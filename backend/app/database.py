"""
数据库配置文件
配置SQLAlchemy引擎、会话和基础模型类
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 计算后端目录，构造默认数据库的绝对路径，避免受工作目录影响
BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BACKEND_DIR / "travel_planner.db"

# 获取数据库URL（优先环境变量），否则使用绝对路径的 SQLite 文件
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=True  # 开发阶段显示SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

def get_db():
    """
    获取数据库会话
    用于依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    创建所有数据表
    """
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")

def drop_tables():
    """
    删除所有数据表（开发阶段使用）
    """
    Base.metadata.drop_all(bind=engine)
    print("数据库表删除完成")