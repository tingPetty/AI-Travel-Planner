"""
AI Travel Planner - FastAPI Backend
主应用入口文件
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, itinerary, budget, speech_recognition, text_parse
import uvicorn

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