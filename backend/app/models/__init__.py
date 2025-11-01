"""
数据模型包
导入所有数据模型类
"""

from .user import User
from .trip import Trip
from .expense import Expense

# 导出所有模型
__all__ = ["User", "Trip", "Expense"]