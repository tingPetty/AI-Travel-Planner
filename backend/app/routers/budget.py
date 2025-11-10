"""
预算管理相关路由

实现功能：
1. 添加费用记录
2. 获取某行程的费用列表
3. 当前剩余资金计算（预算 - 已花费）
4. AI费用提取（从文本中抽取费用信息）
"""

import os
import json
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from openai import OpenAI

from app.database import get_db
from app.models.trip import Trip
from app.models.expense import Expense
from app.schemas.budget import ExpenseCreate, ExpenseResponse, BudgetSummaryResponse, AIExpenseExtractRequest, AIBudgetAnalysisResponse
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/add", response_model=ExpenseResponse)
async def add_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    """添加费用记录到指定行程。"""
    # 校验行程存在
    trip = db.query(Trip).filter(Trip.id == payload.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    # 解析日期
    try:
        expense_dt = datetime.strptime(payload.expense_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=422, detail="expense_date需为YYYY-MM-DD格式")

    # 类别校验
    allowed_categories = {"transport", "accommodation", "food", "entertainment", "shopping", "other"}
    if payload.category not in allowed_categories:
        raise HTTPException(status_code=422, detail="category不在允许范围: transport/accommodation/food/entertainment/shopping/other")

    # 创建费用记录
    expense = Expense(
        trip_id=payload.trip_id,
        amount=payload.amount,
        category=payload.category,
        description=payload.description,
        expense_date=expense_dt,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return ExpenseResponse(
        id=expense.id,
        trip_id=expense.trip_id,
        amount=float(expense.amount),
        category=expense.category,
        description=expense.description,
        expense_date=expense.expense_date,
        created_at=expense.created_at,
    )


@router.get("/list", response_model=List[ExpenseResponse])
async def get_expenses(
    trip_id: int = Query(..., description="行程ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定行程的费用列表（仅限当前用户拥有的行程）。"""
    # 校验行程存在且归属当前用户
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在或无权限")

    expenses = (
        db.query(Expense)
        .filter(Expense.trip_id == trip_id)
        .order_by(Expense.expense_date.asc())
        .all()
    )
    return [
        ExpenseResponse(
            id=e.id,
            trip_id=e.trip_id,
            amount=float(e.amount),
            category=e.category,
            description=e.description,
            expense_date=e.expense_date,
            created_at=e.created_at,
        )
        for e in expenses
    ]


@router.get("/summary", response_model=BudgetSummaryResponse)
async def get_budget_summary(trip_id: int = Query(..., description="行程ID"), db: Session = Depends(get_db)):
    """根据行程预算与费用记录计算剩余资金。"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    expenses = db.query(Expense).filter(Expense.trip_id == trip_id).all()
    total_expenses = sum(float(e.amount) for e in expenses)
    total_budget = float(trip.budget) if trip.budget is not None else None
    remaining_budget = (total_budget - total_expenses) if total_budget is not None else None

    return BudgetSummaryResponse(
        trip_id=trip_id,
        total_budget=total_budget,
        total_expenses=total_expenses,
        remaining_budget=remaining_budget,
    )


def build_expense_prompt(user_text: str) -> str:
    """构建用于费用抽取的提示词。"""
    return f"""
从以下文本中严格提取一条费用记录信息，并以JSON格式返回：

文本：
{user_text}

需要返回的字段（若无则为null）：
1. amount: 金额（浮点数，单位为元，将诸如“100元”、“一百块”、“1千”等转换为数字）
2. category: 费用类别（字符串，请在 交通/住宿/食物/娱乐/购物/其他 中选择一个）
3. description: 费用描述（字符串，如“打车到酒店”、“在xx店铺吃午餐”）
4. expense_date: 发生日期（字符串，格式为YYYY-MM-DD，如：2025-09-10）

注意：
- 仅返回JSON，不要其他文字；
- 若未提到某个字段，返回null；
- ”费用类别“字段必须要在交通/住宿/食物/娱乐/购物/其他 中选择一个，不要自己创造别的值；
- 金额单位转换（万→10000，千→1000，中文数字→阿拉伯数字）。
- “费用时间”字段需要从语义中提取具体日期，如”10月1日”，“10月10日”，“10月10号”等，若年份若未说明则统一为2025年，若实在无法确定则返回null。

示例返回：
{{
  "amount": 35.5,
  "category": "食物",
  "description": "晚餐",
  "expense_date": "2025-10-01"
}}
"""


@router.post("/ai-extract")
async def ai_expense_extract(request: AIExpenseExtractRequest):
    """AI费用提取：从文本中抽取费用信息并返回严格JSON。"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="环境变量缺失：DASHSCOPE_API_KEY")

    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout=60.0,
    )
    model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")

    system_prompt = (
        "你是一个擅长从文本中抽取结构化费用信息的助手。"
        "请严格只输出符合给定字段的JSON，不要任何其他文字。"
    )

    prompt = build_expense_prompt(request.text)

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
                "amount": None,
                "category": None,
                "description": None,
                "expense_date": None,
            }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"调用AI解析失败: {str(e)}")


def build_budget_analysis_prompt(total_budget: Optional[float], total_expenses: float, remaining_budget: Optional[float], expenses: List[Expense]) -> str:
    """构建用于预算分析的提示词。"""
    # 类别中文映射
    category_labels = {
        'transport': '交通',
        'accommodation': '住宿',
        'food': '食物',
        'entertainment': '娱乐',
        'shopping': '购物',
        'other': '其他'
    }
    
    # 按类别统计开销
    category_expenses = {}
    for expense in expenses:
        cat = expense.category
        if cat not in category_expenses:
            category_expenses[cat] = 0
        category_expenses[cat] += float(expense.amount)
    
    # 构建开销明细（使用中文类别）
    expense_details = "\n".join([
        f"- {expense.expense_date.strftime('%Y-%m-%d')}: {category_labels.get(expense.category, expense.category)} - ¥{float(expense.amount):.2f} ({expense.description or '无描述'})"
        for expense in expenses
    ])
    
    # 构建类别统计（使用中文类别）
    category_summary = "\n".join([
        f"- {category_labels.get(cat, cat)}: ¥{amount:.2f}"
        for cat, amount in category_expenses.items()
    ])
    
    budget_info = f"总预算: ¥{total_budget:.2f}" if total_budget is not None else "总预算: 未设置"
    remaining_info = f"剩余资金: ¥{remaining_budget:.2f}" if remaining_budget is not None else "剩余资金: 未设置"
    
    return f"""
你是一位专业的旅游预算分析师。请根据以下信息对当前行程的开销进行分析，并给出三条实用的旅游开销建议。

## 预算信息
{budget_info}
已花费: ¥{total_expenses:.2f}
{remaining_info}

## 开销明细
{expense_details}

## 各类别开销汇总
{category_summary}

## 任务要求
1. 对当前的开销情况进行简要分析（100字以内），包括：
   - 开销是否合理
   - 各类别支出占比情况
   - 预算使用情况（如果有预算）

2. 给出三条具体的旅游开销建议，每条建议应该：
   - 针对性强，基于当前开销数据
   - 实用可行
   - 简洁明了（每条30字以内）

## 输出格式
请严格按照以下JSON格式输出，不要包含其他文字：
{{
  "analysis": "这里是开销分析内容",
  "suggestions": [
    "建议1",
    "建议2",
    "建议3"
  ]
}}
"""


@router.get("/ai-analysis", response_model=AIBudgetAnalysisResponse)
async def ai_budget_analysis(
    trip_id: int = Query(..., description="行程ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI预算分析：分析当前行程的开销情况并给出建议。"""
    # 校验行程存在且归属当前用户
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在或无权限")
    
    # 获取费用记录
    expenses = db.query(Expense).filter(Expense.trip_id == trip_id).order_by(Expense.expense_date.asc()).all()
    
    if not expenses:
        raise HTTPException(status_code=400, detail="当前行程暂无开销记录，无法进行分析")
    
    # 计算预算汇总
    total_expenses = sum(float(e.amount) for e in expenses)
    total_budget = float(trip.budget) if trip.budget is not None else None
    remaining_budget = (total_budget - total_expenses) if total_budget is not None else None
    
    # 调用AI分析
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="环境变量缺失：DASHSCOPE_API_KEY")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        timeout=60.0,
    )
    model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")
    
    system_prompt = (
        "你是一位专业的旅游预算分析师，擅长分析旅游开销并给出实用建议。"
        "请严格按照要求的JSON格式输出，不要包含其他文字。"
    )
    
    prompt = build_budget_analysis_prompt(total_budget, total_expenses, remaining_budget, expenses)
    
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
        
        # 解析JSON响应
        try:
            result = json.loads(content)
            return AIBudgetAnalysisResponse(
                analysis=result.get("analysis", "分析结果解析失败"),
                suggestions=result.get("suggestions", ["建议1", "建议2", "建议3"])
            )
        except json.JSONDecodeError:
            # 尝试从响应中提取JSON
            start_idx = content.find("{")
            end_idx = content.rfind("}")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx : end_idx + 1]
                try:
                    result = json.loads(json_str)
                    return AIBudgetAnalysisResponse(
                        analysis=result.get("analysis", "分析结果解析失败"),
                        suggestions=result.get("suggestions", ["建议1", "建议2", "建议3"])
                    )
                except Exception:
                    pass
            # 如果无法解析，返回默认值
            return AIBudgetAnalysisResponse(
                analysis="AI分析结果解析失败，请稍后重试",
                suggestions=["建议1", "建议2", "建议3"]
            )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"调用AI分析失败: {str(e)}")