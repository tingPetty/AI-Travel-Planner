"""
预算管理相关路由
"""

from fastapi import APIRouter

router = APIRouter()

@router.post("/add")
async def add_expense():
    """添加费用记录"""
    return {"message": "添加费用记录接口 - 待实现"}

@router.get("/list")
async def get_expenses():
    """获取费用列表"""
    return {"message": "获取费用列表接口 - 待实现"}

@router.get("/summary")
async def get_budget_summary():
    """获取预算汇总"""
    return {"message": "获取预算汇总接口 - 待实现"}