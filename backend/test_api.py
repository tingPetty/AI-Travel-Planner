#!/usr/bin/env python3
"""
API测试脚本
测试后端API接口是否正常工作
"""

import requests
import json
from datetime import datetime, timedelta

# API基础URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """测试健康检查接口"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"健康检查: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_user_registration():
    """测试用户注册"""
    try:
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        print(f"用户注册: {response.status_code} - {response.json()}")
        return response.status_code in [200, 201, 400]  # 400可能是用户已存在
    except Exception as e:
        print(f"用户注册失败: {e}")
        return False

def test_user_login():
    """测试用户登录"""
    try:
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
        print(f"用户登录: {response.status_code} - {response.json()}")
        
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except Exception as e:
        print(f"用户登录失败: {e}")
        return None

def test_itinerary_generation(token):
    """测试行程生成接口"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # 计算日期
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        
        itinerary_data = {
            "title": "测试行程",
            "destination": "北京",
            "start_date": start_date,
            "end_date": end_date,
            "budget": 5000,
            "preferences": "美食, 文化",
            "travelers": 2
        }
        
        response = requests.post(
            f"{BASE_URL}/api/itinerary/generate", 
            json=itinerary_data,
            headers=headers
        )
        print(f"行程生成: {response.status_code} - {response.json()}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"行程生成失败: {e}")
        return False

def test_itinerary_list(token):
    """测试行程列表接口"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/itinerary/", headers=headers)
        print(f"行程列表: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"行程列表失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始API测试...")
    print("=" * 50)
    
    # 测试健康检查
    if not test_health_check():
        print("❌ 健康检查失败，请确保后端服务正在运行")
        return
    
    print("✅ 健康检查通过")
    
    # 测试用户注册
    test_user_registration()
    print("✅ 用户注册测试完成")
    
    # 测试用户登录
    token = test_user_login()
    if not token:
        print("❌ 用户登录失败")
        return
    
    print("✅ 用户登录成功")
    
    # 测试行程列表
    if test_itinerary_list(token):
        print("✅ 行程列表接口正常")
    else:
        print("❌ 行程列表接口异常")
    
    # 测试行程生成（可能因为缺少API密钥而失败）
    if test_itinerary_generation(token):
        print("✅ 行程生成接口正常")
    else:
        print("⚠️  行程生成接口异常（可能需要配置API密钥）")
    
    print("=" * 50)
    print("API测试完成")

if __name__ == "__main__":
    main()