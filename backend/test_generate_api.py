"""
测试行程生成API的数据格式
"""

import requests
import json
import random
import string

def get_auth_token():
    """注册用户并获取认证token"""
    # 生成随机用户名
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    username = f"testuser_{random_suffix}"
    email = f"{username}@example.com"
    
    register_data = {
        "username": username,
        "email": email,
        "password": "testpass123"
    }
    
    print(f"注册用户: {username}")
    
    try:
        response = requests.post("http://localhost:8000/api/auth/register", json=register_data)
        if response.status_code == 201:
            result = response.json()
            token = result.get("access_token")
            print(f"✅ 注册成功，获取token: {token[:20]}...")
            return token
        else:
            print(f"❌ 注册失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 注册异常: {e}")
        return None

def test_generate_api():
    """测试行程生成API"""
    
    # 获取认证token
    token = get_auth_token()
    if not token:
        print("无法获取认证token，测试终止")
        return
    
    # 模拟前端发送的数据
    test_data = {
        "title": "南京旅游",
        "destination": "南京",
        "start_date": "2025-11-01",
        "end_date": "2025-11-04",
        "budget": 1000,
        "preferences": "美食, 文化, 自然风光",
        "travel_style": "休闲度假"
    }
    
    print("\n测试数据:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    print()
    
    # 发送请求
    url = "http://localhost:8000/api/itinerary/generate"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        print("发送请求到:", url)
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print()
        
        if response.status_code == 422:
            print("❌ 422 验证错误:")
            print(response.text)
        elif response.status_code == 200:
            print("✅ 请求成功:")
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ 其他错误 ({response.status_code}):")
            print(response.text)
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_generate_api()