"""
行程模型
包含旅行计划基本信息和详细行程安排
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Trip(Base):
    """
    行程表模型
    存储旅行计划主表和详细行程
    """
    __tablename__ = "trips"
    
    # 基本字段
    id = Column(Integer, primary_key=True, index=True, comment="行程ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    title = Column(String(200), nullable=False, comment="行程标题")
    destination = Column(String(100), nullable=False, comment="目的地")
    start_date = Column(DateTime, nullable=False, comment="开始日期")
    end_date = Column(DateTime, nullable=False, comment="结束日期")
    budget = Column(Numeric(10, 2), nullable=True, comment="预算金额")
    travelers = Column(Integer, nullable=True, comment="旅行人数")
    status = Column(String(20), default="planning", comment="行程状态: planning, ongoing, completed, cancelled")
    
    # 详细字段 (JSON格式存储)
    itinerary = Column(JSON, nullable=True, comment="详细行程安排")
    
    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系映射
    user = relationship("User", back_populates="trips")
    expenses = relationship("Expense", back_populates="trip", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Trip(id={self.id}, title='{self.title}', destination='{self.destination}', status='{self.status}')>"
    
    def to_dict(self):
        """
        转换为字典格式
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "destination": self.destination,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "budget": float(self.budget) if self.budget else None,
            "travelers": self.travelers,
            "status": self.status,
            "itinerary": self.itinerary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def duration_days(self):
        """
        计算行程天数
        """
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0