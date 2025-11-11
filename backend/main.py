"""
AI Travel Planner - FastAPI Backend
主应用入口文件
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, itinerary, budget, speech_recognition, text_parse
import uvicorn

# 加载.env文件中的环境变量
# import logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # 显示当前工作目录和.env文件路径
# current_dir = os.getcwd()
# env_file_path = os.path.join(current_dir, '.env')
# logger.info(f"当前工作目录: {current_dir}")
# logger.info(f"查找.env文件路径: {env_file_path}")
# logger.info(f".env文件是否存在: {os.path.exists(env_file_path)}")

# 加载.env文件（使用override=True强制覆盖系统环境变量）
load_result = load_dotenv(override=True)
# logger.info(f"load_dotenv()执行结果: {load_result}")
# logger.info("使用 override=True 强制覆盖系统环境变量")

# # 显示加载后的关键环境变量
# logger.info(f"加载后的ALIYUN_TOKEN: {os.getenv('ALIYUN_TOKEN')}")
# logger.info(f"加载后的ALIYUN_APP_KEY: {os.getenv('ALIYUN_APP_KEY')}")

# 创建 FastAPI 应用实例
app = FastAPI(
    title="AI Travel Planner API",
    description="智能旅行规划师后端API",
    version="1.0.0"
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue 开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(itinerary.router, prefix="/api/itinerary", tags=["行程规划"])
app.include_router(budget.router, prefix="/api/budget", tags=["预算管理"])
app.include_router(speech_recognition.router, prefix="/api/speech", tags=["语音识别"])
app.include_router(text_parse.router, prefix="/api/text", tags=["文本解析"])

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "AI Travel Planner API",
        "version": "1.0.0",
        "status": "running",
        "description": "智能旅行规划师后端API - Hello World测试成功！"
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.get("/api/test")
async def test_api():
    """API测试接口"""
    return {
        "message": "Hello World from FastAPI!",
        "status": "success",
        "features": [
            "FastAPI框架",
            "自动API文档",
            "CORS支持",
            "路由系统"
        ]
    }

@app.get("/api/test/echo/{message}")
async def echo_message(message: str):
    """回声测试接口"""
    return {
        "original_message": message,
        "echo": f"Echo: {message}",
        "length": len(message)
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )