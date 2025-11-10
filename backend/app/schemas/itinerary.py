"""
行程相关的数据模式
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class ItineraryGenerateRequest(BaseModel):
    """生成行程请求模型"""
    destination: str = Field(..., description="目的地", min_length=1, max_length=100)
    start_date: str = Field(..., description="开始日期 (YYYY-MM-DD)", pattern=r'^\d{4}-\d{2}-\d{2}$')
    end_date: str = Field(..., description="结束日期 (YYYY-MM-DD)", pattern=r'^\d{4}-\d{2}-\d{2}$')
    budget: Optional[float] = Field(None, description="预算金额", ge=0)
    preferences: Optional[str] = Field(None, description="用户偏好", max_length=500)
    travelers: Optional[int] = Field(None, description="旅行人数", ge=1)
    title: Optional[str] = Field(None, description="行程标题", max_length=200)

class ItineraryUpdateRequest(BaseModel):
    """更新行程请求模型"""
    title: Optional[str] = Field(None, description="行程标题", max_length=200)
    destination: Optional[str] = Field(None, description="目的地", max_length=100)
    start_date: Optional[str] = Field(None, description="开始日期 (YYYY-MM-DD)", pattern=r'^\d{4}-\d{2}-\d{2}$')
    end_date: Optional[str] = Field(None, description="结束日期 (YYYY-MM-DD)", pattern=r'^\d{4}-\d{2}-\d{2}$')
    budget: Optional[float] = Field(None, description="预算金额", ge=0)
    travelers: Optional[int] = Field(None, description="旅行人数", ge=1)
    status: Optional[str] = Field(None, description="行程状态")
    itinerary: Optional[Dict[str, Any]] = Field(None, description="详细行程")

class ActivityModel(BaseModel):
    """活动模型"""
    time: str = Field(..., description="时间")
    activity: str = Field(..., description="活动名称")
    location: str = Field(..., description="地点")
    duration: str = Field(..., description="持续时间")
    cost: float = Field(..., description="费用")
    type: Optional[str] = Field(None, description="活动类型")
    description: Optional[str] = Field(None, description="活动描述")

class DayItineraryModel(BaseModel):
    """单日行程模型"""
    date: str = Field(..., description="日期")
    activities: List[ActivityModel] = Field(..., description="活动列表")

class ItineraryResponse(BaseModel):
    """行程响应模型"""
    id: int = Field(..., description="行程ID")
    user_id: int = Field(..., description="用户ID")
    title: str = Field(..., description="行程标题")
    destination: str = Field(..., description="目的地")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    budget: Optional[float] = Field(None, description="预算金额")
    travelers: Optional[int] = Field(None, description="旅行人数")
    status: str = Field(..., description="行程状态")
    itinerary: Optional[Dict[str, Any]] = Field(None, description="详细行程")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

class ItineraryListResponse(BaseModel):
    """行程列表响应模型"""
    id: int = Field(..., description="行程ID")
    title: str = Field(..., description="行程标题")
    destination: str = Field(..., description="目的地")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    travelers: Optional[int] = Field(None, description="旅行人数")
    status: str = Field(..., description="行程状态")
    created_at: datetime = Field(..., description="创建时间")

class GenerateItineraryResponse(BaseModel):
    """生成行程响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[ItineraryResponse] = Field(None, description="行程数据")
    
class APIResponse(BaseModel):
    """通用API响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")