"""
文本解析路由：调用通义千问（DashScope 兼容接口）解析上传文本并提取行程信息。

从请求文本中抽取 destination、title、start_date、end_date、budget、travelers、preferences。
仅返回JSON，不含其他解释。
"""

import os
import json
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI


router = APIRouter()


class TextParseRequest(BaseModel):
    text: str


def build_prompt(user_text: str) -> str:
    """构建用于信息抽取的提示词。"""
    return f"""
从上传的文本中提取旅行规划信息，并以JSON格式返回。

文本具体内容：
{user_text}

请提取以下信息（如果文本中没有提到某项信息，则该字段返回null）：
1. destination: 目的地（字符串，如"日本"、"东京"）
2. title: 根据用户的行程内容生成的一个简短标题，10字以内。（字符串，如“南京之旅”、“北京三日游”）
3. start_date: 出发日期（字符串，格式YYYY-MM-DD，如"2023-03-25"）
4. end_date: 结束日期（字符串，格式YYYY-MM-DD，如"2023-12-27"，如果用户没有具体给出，需要你通过出发日期和天数自行计算）
5. budget: 预算金额（浮点数，单位为元，将"一万元"、"1万元"转换为10000）
6. travelers: 旅行人数（整数，将"两人"、"2人"等转换为数字2）
7. preferences: 旅行偏好（字符串，多个偏好用顿号分隔，如"美食、动漫文化"）

注意：
- 中文数字要转换为阿拉伯数字（一、二、三 → 1、2、3）
- 金额单位转换（万→10000，千→1000）
- 偏好关键词规范化（如：吃→美食，孩子→亲子游，不喜欢早起→悠闲或懒人游）
- 日期转换：
  * "明天"、"后天" → 计算具体日期
  * "下周一"、"下个月1号" → 计算具体日期
  * "12月25号"、"12月25日" → 转换为当年的2024-12-25格式
  * 只给出了出发日期和游玩天数 → 自行计算结束日期
  * "元旦"、"春节"、"国庆" → 转换为对应的具体日期
  * 如果只说"月日"没说年份，默认是2025年（就近原则）

只返回JSON，不要其他解释。格式如下：
{{
  "destination": "目的地或null",
  "title": "标题或null",
  "start_date": "YYYY-MM-DD格式日期或null",
  "end_date": "YYYY-MM-DD格式日期或null",
  "budget": 预算数字或null,
  "travelers": 人数数字或null,
  "preferences": "偏好或null"
}}
"""


@router.post("/parse")
async def parse_text(request: TextParseRequest):
    """解析上传文本，返回旅行规划信息JSON。"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="环境变量缺失：DASHSCOPE_API_KEY")

    # 使用 DashScope 兼容模式
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout=60.0,
    )
    model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")

    system_prompt = (
        "你是一个擅长从文本中抽取结构化信息的助手。"
        "请严格只输出符合给定字段的JSON，不要任何其他文字。"
    )

    prompt = build_prompt(request.text)

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        content = completion.choices[0].message.content

        # 只返回JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # 尝试从响应中提取JSON
            start_idx = content.find("{")
            end_idx = content.rfind("}")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx : end_idx + 1]
                try:
                    return json.loads(json_str)
                except Exception:
                    pass
            # 如果无法解析，返回字段全部null
            return {
                "destination": None,
                "title": None,
                "start_date": None,
                "end_date": None,
                "budget": None,
                "travelers": None,
                "preferences": None,
            }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"调用AI解析失败: {str(e)}")