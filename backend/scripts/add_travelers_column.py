"""
SQLite 变更脚本：为 trips 表添加 travelers 列

使用方法：
1) 确保已配置环境变量 `DATABASE_URL`（默认 sqlite:///./travel_planner.db）
2) 在项目根目录运行：
   python backend/scripts/add_travelers_column.py
"""

import os
from sqlalchemy import text
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from app.database import engine

def column_exists(conn, table_name: str, column_name: str) -> bool:
    result = conn.execute(text(f"PRAGMA table_info({table_name})")).mappings().all()
    for row in result:
        if row.get("name") == column_name:
            return True
    return False

def add_travelers_column():
    with engine.begin() as conn:
        if column_exists(conn, "trips", "travelers"):
            print("✅ 列 travelers 已存在，跳过变更")
            return
        print("➡️ 正在为 trips 表添加 travelers 列 (INTEGER, 可空)...")
        conn.execute(text("ALTER TABLE trips ADD COLUMN travelers INTEGER"))
        print("✅ 添加完成")

if __name__ == "__main__":
    add_travelers_column()