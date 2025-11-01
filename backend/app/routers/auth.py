"""
用户认证相关路由
"""

from fastapi import APIRouter

router = APIRouter()

@router.post("/register")
async def register():
    """用户注册"""
    return {"message": "用户注册接口 - 待实现"}

@router.post("/login")
async def login():
    """用户登录"""
    return {"message": "用户登录接口 - 待实现"}

@router.post("/logout")
async def logout():
    """用户登出"""
    return {"message": "用户登出接口 - 待实现"}