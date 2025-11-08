#!/usr/bin/env python3
"""
简单的API测试脚本
"""

import requests
import json

def test_api():
    """测试行程生成API"""
    
    # 1. 注册用户获取token
    register_data = {
        "username": "testuser456",
        "email": "testuser456@example.com",
        "password": "testpass123"
    }
    
    try:
        # 注册用户
        register_response = requests.post(
            "http://localhost:8000/api/auth/register",
            json=register_data
        )
        
        if register_response.status_code in [200, 201]:
            token = register_response.json()["access_token"]
            print(f"✅ 用户注册成功，获取token: {token[:20]}...")
        else:
            print(f"❌ 用户注册失败: {register_response.status_code}")
            print(register_response.text)
            return
            
    except Exception as e:
        print(f"❌ 注册请求失败: {e}")
        return
    
    # 2. 测试行程生成API
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    itinerary_data = {
        "title": "南京旅游",
        "destination": "南京",
        "start_date": "2025-11-01",
        "end_date": "2025-11-04",
        "budget": 1000,
        "preferences": "美食, 文化, 自然风光",
        "travel_style": "休闲度假"
    }
    
    print(f"📤 发送行程生成请求...")
    print(f"请求数据: {json.dumps(itinerary_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/itinerary/generate",
            json=itinerary_data,
            headers=headers,
            timeout=60  # 60秒超时
        )
        
        print(f"📥 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API调用成功!")
            print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"错误详情: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    test_api()