"""
行程规划相关路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.trip import Trip
from app.schemas.itinerary import (
    ItineraryGenerateRequest, 
    ItineraryUpdateRequest,
    ItineraryResponse, 
    ItineraryListResponse,
    GenerateItineraryResponse,
    APIResponse
)
from app.services.ai_service import ai_service
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/generate", response_model=GenerateItineraryResponse)
async def generate_itinerary(
    request: ItineraryGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成行程规划"""
    try:
        # 验证日期
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
        
        if start_date >= end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束日期必须晚于开始日期"
            )
        
        # 调用AI服务生成行程
        ai_result = ai_service.generate_itinerary(
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            budget=request.budget,
            preferences=request.preferences,
            travel_style=request.travel_style
        )
        
        if not ai_result["success"]:
            return GenerateItineraryResponse(
                success=False,
                message=ai_result["message"],
                data=None
            )
        
        # 生成行程标题
        title = request.title or f"{request.destination}之旅"
        
        # 保存到数据库
        trip = Trip(
            user_id=current_user.id,
            title=title,
            destination=request.destination,
            start_date=start_date,
            end_date=end_date,
            budget=request.budget,
            status="planning",
            itinerary=ai_result["data"]
        )
        
        db.add(trip)
        db.commit()
        db.refresh(trip)
        
        # 构建响应
        trip_response = ItineraryResponse(
            id=trip.id,
            user_id=trip.user_id,
            title=trip.title,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            budget=trip.budget,
            status=trip.status,
            itinerary=trip.itinerary,
            created_at=trip.created_at,
            updated_at=trip.updated_at
        )
        
        return GenerateItineraryResponse(
            success=True,
            message="行程生成成功",
            data=trip_response
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="日期格式不正确，请使用YYYY-MM-DD格式"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成行程失败: {str(e)}"
        )

@router.get("/list", response_model=List[ItineraryListResponse])
async def get_itineraries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的行程列表"""
    trips = db.query(Trip).filter(Trip.user_id == current_user.id).order_by(Trip.created_at.desc()).all()
    
    return [
        ItineraryListResponse(
            id=trip.id,
            title=trip.title,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            status=trip.status,
            created_at=trip.created_at
        )
        for trip in trips
    ]

@router.get("/{itinerary_id}", response_model=ItineraryResponse)
async def get_itinerary(
    itinerary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个行程详情"""
    trip = db.query(Trip).filter(
        Trip.id == itinerary_id,
        Trip.user_id == current_user.id
    ).first()
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="行程不存在"
        )
    
    return ItineraryResponse(
        id=trip.id,
        user_id=trip.user_id,
        title=trip.title,
        destination=trip.destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
        budget=trip.budget,
        status=trip.status,
        itinerary=trip.itinerary,
        created_at=trip.created_at,
        updated_at=trip.updated_at
    )

@router.put("/{itinerary_id}", response_model=APIResponse)
async def update_itinerary(
    itinerary_id: int,
    request: ItineraryUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新行程"""
    trip = db.query(Trip).filter(
        Trip.id == itinerary_id,
        Trip.user_id == current_user.id
    ).first()
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="行程不存在"
        )
    
    try:
        # 更新基本信息
        if request.title is not None:
            trip.title = request.title
        if request.destination is not None:
            trip.destination = request.destination
        if request.budget is not None:
            trip.budget = request.budget
        if request.status is not None:
            trip.status = request.status
        if request.itinerary is not None:
            trip.itinerary = request.itinerary
            
        # 验证和更新日期
        if request.start_date is not None:
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
            trip.start_date = start_date
            
        if request.end_date is not None:
            end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
            trip.end_date = end_date
            
        # 验证日期逻辑
        if trip.start_date >= trip.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束日期必须晚于开始日期"
            )
        
        db.commit()
        
        return APIResponse(
            success=True,
            message="行程更新成功"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="日期格式不正确，请使用YYYY-MM-DD格式"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新行程失败: {str(e)}"
        )

@router.delete("/{itinerary_id}", response_model=APIResponse)
async def delete_itinerary(
    itinerary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除行程"""
    trip = db.query(Trip).filter(
        Trip.id == itinerary_id,
        Trip.user_id == current_user.id
    ).first()
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="行程不存在"
        )
    
    db.delete(trip)
    db.commit()
    
    return APIResponse(
        success=True,
        message="行程删除成功"
    )