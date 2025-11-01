"""
数据库查看脚本
查看数据库中的数据
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User, Trip, Expense

def view_database():
    """查看数据库中的所有数据"""
    db = SessionLocal()
    
    try:
        print("=" * 50)
        print("数据库数据查看")
        print("=" * 50)
        
        # 查看用户数据
        print("\n📋 用户数据:")
        users = db.query(User).all()
        for user in users:
            print(f"  ID: {user.id}")
            print(f"  用户名: {user.username}")
            print(f"  邮箱: {user.email}")
            print(f"  偏好设置: {user.preferences}")
            print(f"  创建时间: {user.created_at}")
            print("-" * 30)
        
        # 查看行程数据
        # print("\n🗺️ 行程数据:")
        # trips = db.query(Trip).all()
        # for trip in trips:
        #     print(f"  ID: {trip.id}")
        #     print(f"  用户ID: {trip.user_id}")
        #     print(f"  标题: {trip.title}")
        #     print(f"  目的地: {trip.destination}")
        #     print(f"  开始日期: {trip.start_date}")
        #     print(f"  结束日期: {trip.end_date}")
        #     print(f"  预算: {trip.budget}")
        #     print(f"  状态: {trip.status}")
        #     print(f"  行程天数: {trip.duration_days}")
        #     print(f"  详细行程: {trip.itinerary}")
        #     print("-" * 30)
        
        # # 查看费用数据
        # print("\n💰 费用记录:")
        # expenses = db.query(Expense).all()
        # for expense in expenses:
        #     print(f"  ID: {expense.id}")
        #     print(f"  行程ID: {expense.trip_id}")
        #     print(f"  金额: {expense.amount}")
        #     print(f"  类别: {expense.category} ({expense.category_display})")
        #     print(f"  描述: {expense.description}")
        #     print(f"  费用日期: {expense.expense_date}")
        #     print(f"  创建时间: {expense.created_at}")
        #     print("-" * 30)
        
        # # 统计信息
        # print("\n📊 统计信息:")
        # print(f"  总用户数: {len(users)}")
        # print(f"  总行程数: {len(trips)}")
        # print(f"  总费用记录数: {len(expenses)}")
        
        # # 计算总费用
        # total_expenses = sum(float(expense.amount) for expense in expenses)
        # print(f"  总费用金额: ¥{total_expenses:.2f}")
        
    except Exception as e:
        print(f"查看数据库时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    view_database()