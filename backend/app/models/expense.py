"""
费用记录模型
记录旅行中的各项支出
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Expense(Base):
    """
    费用记录表模型
    记录旅行中的各项支出
    """
    __tablename__ = "expenses"
    
    # 基本字段
    id = Column(Integer, primary_key=True, index=True, comment="费用记录ID")
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, comment="行程ID")
    amount = Column(Numeric(10, 2), nullable=False, comment="金额")
    category = Column(String(50), nullable=False, comment="费用类别: transport, accommodation, food, entertainment, shopping, other")
    description = Column(Text, nullable=True, comment="费用描述")
    expense_date = Column(DateTime, nullable=False, comment="费用发生日期")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关系映射
    trip = relationship("Trip", back_populates="expenses")
    
    def __repr__(self):
        return f"<Expense(id={self.id}, trip_id={self.trip_id}, amount={self.amount}, category='{self.category}')>"
    
    def to_dict(self):
        """
        转换为字典格式
        """
        return {
            "id": self.id,
            "trip_id": self.trip_id,
            "amount": float(self.amount) if self.amount else None,
            "category": self.category,
            "description": self.description,
            "expense_date": self.expense_date.isoformat() if self.expense_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @property
    def category_display(self):
        """
        费用类别显示名称
        """
        category_map = {
            "transport": "交通",
            "accommodation": "住宿",
            "food": "餐饮",
            "entertainment": "娱乐",
            "shopping": "购物",
            "other": "其他"
        }
        return category_map.get(self.category, self.category)