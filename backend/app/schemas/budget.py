"""
预算与费用相关的数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ExpenseCreate(BaseModel):
    """添加费用请求模型"""
    trip_id: int = Field(..., description="行程ID")
    amount: float = Field(..., ge=0, description="金额，以元为单位")
    category: str = Field(..., description="费用类别: transport, accommodation, food, entertainment, shopping, other")
    description: Optional[str] = Field(None, description="费用描述")
    expense_date: str = Field(..., description="费用日期 (YYYY-MM-DD)")


class ExpenseResponse(BaseModel):
    """费用记录响应模型"""
    id: int
    trip_id: int
    amount: float
    category: str
    description: Optional[str]
    expense_date: datetime
    created_at: datetime


class BudgetSummaryResponse(BaseModel):
    """预算汇总响应模型"""
    trip_id: int
    total_budget: Optional[float] = Field(None, description="行程预算，可能为空")
    total_expenses: float = Field(..., description="总开销")
    remaining_budget: Optional[float] = Field(None, description="剩余预算，预算为空时返回null")


class AIExpenseExtractRequest(BaseModel):
    """AI费用提取请求模型"""
    text: str = Field(..., description="需要解析的原始文本")


class AIBudgetAnalysisResponse(BaseModel):
    """AI预算分析响应模型"""
    analysis: str = Field(..., description="预算分析结果")
    suggestions: list[str] = Field(..., description="三条旅游开销建议")