#!/usr/bin/env python3
# coding=utf-8
"""
控制台输入文本，调用后端 /api/text/parse 接口，让AI解析并返回行程信息JSON。

运行前请确保：
- 后端已启动（例如：python -m uvicorn backend.main:app --reload）
- 已配置环境变量 DASHSCOPE_API_KEY（用于调用DashScope兼容模式）
"""

import os
import json
import requests

# 可选：自动加载 backend/.env
try:
    from dotenv import load_dotenv
    _env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))
    if os.path.exists(_env_path):
        load_dotenv(_env_path)
    else:
        load_dotenv()
except Exception:
    pass


BASE_URL = os.getenv("TEXT_PARSE_BASE_URL", "http://localhost:8000")


def main():
    print("请输入要解析的文本（按回车提交）：")
    user_text = input().strip()
    if not user_text:
        print("输入为空，已退出")
        return

    url = f"{BASE_URL}/api/text/parse"
    payload = {"text": user_text}

    try:
        resp = requests.post(url, json=payload, timeout=60)
        print(f"状态码: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print("解析结果:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print("请求失败:")
            print(resp.text)
    except Exception as e:
        print(f"请求异常: {e}")


if __name__ == "__main__":
    main()