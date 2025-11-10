"""
预算与费用接口测试脚本

依次测试：
1) 添加费用记录 (/api/budget/add)
2) 获取费用列表 (/api/budget/list)
3) 预算汇总 (/api/budget/summary)
4) AI费用提取 (/api/budget/ai-extract) —— 文本由终端输入

使用方法：
- 请先在终端启动后端服务：python backend/start.py 或 uvicorn main:app --reload
- 然后运行本脚本：python codetest/test_budget_api.py
"""

import sys
import json
import time
from typing import Any, Dict

import requests


DEFAULT_BASE = "http://localhost:8000"
API_BASE = DEFAULT_BASE + "/api"


def pretty_print(title: str, data: Any):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    try:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception:
        print(data)


def test_add_expense(trip_id: int):
    payload = {
        "trip_id": trip_id,
        "amount": 88.5,
        "category": "food",
        "description": "测试-午餐",
        "expense_date": time.strftime("%Y-%m-%d"),
    }
    r = requests.post(f"{API_BASE}/budget/add", json=payload)
    r.raise_for_status()
    return r.json()


def test_list_expenses(trip_id: int):
    r = requests.get(f"{API_BASE}/budget/list", params={"trip_id": trip_id})
    r.raise_for_status()
    return r.json()


def test_summary(trip_id: int):
    r = requests.get(f"{API_BASE}/budget/summary", params={"trip_id": trip_id})
    r.raise_for_status()
    return r.json()


def test_ai_extract():
    print("\n请输入需要解析的费用文本（按回车提交）：")
    text = sys.stdin.readline().strip()
    if not text:
        text = "中午和朋友在南京夫子庙吃饭花了150块，昨天打车从机场到酒店80元。"
        print(f"使用默认示例文本：{text}")
    r = requests.post(f"{API_BASE}/budget/ai-extract", json={"text": text})
    r.raise_for_status()
    return r.json()


def main():
    global API_BASE
    print("预算与费用接口测试脚本")
    base = input(f"后端基地址(默认 {DEFAULT_BASE}): ") or DEFAULT_BASE
    API_BASE = base.rstrip("/") + "/api"

    trip_id_str = input("请输入要测试的行程ID(默认1): ") or "1"
    try:
        trip_id = int(trip_id_str)
    except ValueError:
        trip_id = 1

    try:
        # 1) 添加费用记录
        add_res = test_add_expense(trip_id)
        pretty_print("添加费用记录-响应", add_res)

        # 2) 获取费用列表
        list_res = test_list_expenses(trip_id)
        pretty_print("费用列表-响应", list_res)

        # 3) 预算汇总
        sum_res = test_summary(trip_id)
        pretty_print("预算汇总-响应", sum_res)

        # 4) AI费用提取
        ai_res = test_ai_extract()
        pretty_print("AI费用提取-响应", ai_res)

        # 如果AI返回了完整字段，可进一步提示如何添加到指定行程
        if isinstance(ai_res, dict) and ai_res.get("amount") is not None:
            print("\n可将AI返回的字段与trip_id组成payload调用 /budget/add 完成添加。")
    except requests.HTTPError as e:
        print("请求失败:", e)
        if e.response is not None:
            print("状态码:", e.response.status_code)
            try:
                print("响应:", e.response.json())
            except Exception:
                print("响应文本:", e.response.text)


if __name__ == "__main__":
    main()