#!/usr/bin/env python3
"""
测试认证逻辑的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.auth import get_password_hash, verify_password
from app.database import SessionLocal
from app.models.user import User

def test_password_logic():
    """测试密码哈希和验证逻辑"""
    print("=== 密码哈希和验证测试 ===")
    
    # 测试密码
    test_password = "testpassword123"
    
    # 生成哈希
    hashed = get_password_hash(test_password)
    print(f"原始密码: {test_password}")
    print(f"哈希值: {hashed}")
    
    # 验证密码
    is_valid = verify_password(test_password, hashed)
    print(f"验证结果: {is_valid}")
    
    # 测试错误密码
    wrong_password = "wrongpassword"
    is_invalid = verify_password(wrong_password, hashed)
    print(f"错误密码验证结果: {is_invalid}")
    
    return hashed

def check_user_password():
    """检查数据库中用户的密码"""
    print("\n=== 检查数据库用户密码 ===")
    
    db = SessionLocal()
    try:
        # 查找test@example.com用户
        user = db.query(User).filter(User.email == "test@example.com").first()
        if user:
            print(f"找到用户: {user.username} ({user.email})")
            print(f"存储的密码哈希: {user.password_hash}")
            
            # 尝试常见的测试密码
            test_passwords = ["testpassword123", "password", "123456", "test123", "testuser"]
            
            for pwd in test_passwords:
                is_valid = verify_password(pwd, user.password_hash)
                print(f"密码 '{pwd}' 验证结果: {is_valid}")
                if is_valid:
                    print(f"✅ 找到正确密码: {pwd}")
                    return pwd
            
            print("❌ 未找到匹配的密码")
        else:
            print("❌ 未找到用户 test@example.com")
    finally:
        db.close()
    
    return None

def create_test_user():
    """创建一个新的测试用户"""
    print("\n=== 创建测试用户 ===")
    
    db = SessionLocal()
    try:
        # 检查是否已存在
        existing_user = db.query(User).filter(User.email == "testlogin@example.com").first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
            print("删除已存在的测试用户")
        
        # 创建新用户
        password = "testpassword123"
        hashed_password = get_password_hash(password)
        
        new_user = User(
            username="testlogin",
            email="testlogin@example.com",
            password_hash=hashed_password,
            preferences={"theme": "light"}
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ 创建测试用户成功:")
        print(f"   邮箱: testlogin@example.com")
        print(f"   密码: {password}")
        print(f"   用户名: testlogin")
        
        # 验证创建的用户
        verification = verify_password(password, new_user.password_hash)
        print(f"   密码验证: {verification}")
        
    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # 测试密码逻辑
    test_password_logic()
    
    # 检查现有用户密码
    check_user_password()
    
    # 创建新的测试用户
    create_test_user()