"""
认证相关的数据模型
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    """用户注册模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    preferences: Optional[dict] = Field(default={}, description="用户偏好设置")

class UserLogin(BaseModel):
    """用户登录模型"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")

class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    preferences: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: Optional[int] = None