"""
行程规划相关路由
"""

from fastapi import APIRouter

router = APIRouter()

@router.post("/generate")
async def generate_itinerary():
    """生成行程规划"""
    return {"message": "AI行程生成接口 - 待实现"}

@router.get("/list")
async def get_itineraries():
    """获取行程列表"""
    return {"message": "获取行程列表接口 - 待实现"}

@router.get("/{itinerary_id}")
async def get_itinerary(itinerary_id: int):
    """获取单个行程详情"""
    return {"message": f"获取行程{itinerary_id}详情接口 - 待实现"}