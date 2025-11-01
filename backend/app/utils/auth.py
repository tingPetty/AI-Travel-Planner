"""
JWT认证工具类
提供JWT token的生成、验证和密码哈希功能
"""

import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码盐值
PASSWORD_SALT = "travel_planner_salt_2024"

class AuthUtils:
    """认证工具类"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            # 使用相同的方法生成哈希值进行比较
            computed_hash = AuthUtils.get_password_hash(plain_password)
            return computed_hash == hashed_password
        except Exception:
            return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希值"""
        # 使用SHA256和盐值进行哈希
        salted_password = password + PASSWORD_SALT
        return hashlib.sha256(salted_password.encode()).hexdigest()
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[int]:
        """从令牌中获取用户ID"""
        payload = AuthUtils.verify_token(token)
        if payload:
            return payload.get("sub")
        return None

# 便捷函数
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return AuthUtils.verify_password(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希值"""
    return AuthUtils.get_password_hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    return AuthUtils.create_access_token(data, expires_delta)

def verify_token(token: str) -> Optional[dict]:
    """验证令牌"""
    return AuthUtils.verify_token(token)

def get_user_id_from_token(token: str) -> Optional[int]:
    """从令牌中获取用户ID"""
    return AuthUtils.get_user_id_from_token(token)