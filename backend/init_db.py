"""
数据库初始化脚本
创建数据表并插入测试数据
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import create_tables, SessionLocal
from app.models import User, Trip, Expense
import hashlib

def hash_password(password: str) -> str:
    """加密密码 - 简化版本用于测试"""
    # 使用SHA256进行简单加密（生产环境应使用bcrypt）
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    """
    初始化数据库
    创建表结构并插入测试数据
    """
    print("开始初始化数据库...")
    
    # 创建所有表
    create_tables()
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("数据库已有数据，跳过初始化")
            return
        
        print("插入测试数据...")
        
        # 创建测试用户
        test_users = [
            User(
                username="testuser1",
                email="test1@example.com",
                password_hash=hash_password("password123"),
                preferences={
                    "budget_range": "medium",
                    "travel_style": "leisure",
                    "preferred_activities": ["sightseeing", "food", "culture"],
                    "accommodation_type": "hotel",
                    "transport_preference": "public"
                }
            ),
            User(
                username="testuser2",
                email="test2@example.com",
                password_hash=hash_password("password456"),
                preferences={
                    "budget_range": "high",
                    "travel_style": "adventure",
                    "preferred_activities": ["outdoor", "sports", "nature"],
                    "accommodation_type": "resort",
                    "transport_preference": "rental_car"
                }
            )
        ]
        
        # 添加用户到数据库
        for user in test_users:
            db.add(user)
        db.commit()
        
        # 刷新用户对象以获取ID
        for user in test_users:
            db.refresh(user)
        
        # 创建测试行程
        test_trips = [
            Trip(
                user_id=test_users[0].id,
                title="北京三日游",
                destination="北京",
                start_date=datetime.now() + timedelta(days=30),
                end_date=datetime.now() + timedelta(days=32),
                budget=Decimal("3000.00"),
                status="planning",
                itinerary={
                    "day1": {
                        "date": "2024-02-01",
                        "activities": [
                            {
                                "time": "09:00",
                                "activity": "参观天安门广场",
                                "location": "天安门广场",
                                "duration": "2小时",
                                "cost": 0
                            },
                            {
                                "time": "14:00",
                                "activity": "游览故宫博物院",
                                "location": "故宫",
                                "duration": "3小时",
                                "cost": 60
                            }
                        ]
                    },
                    "day2": {
                        "date": "2024-02-02",
                        "activities": [
                            {
                                "time": "08:00",
                                "activity": "登长城",
                                "location": "八达岭长城",
                                "duration": "4小时",
                                "cost": 45
                            }
                        ]
                    },
                    "day3": {
                        "date": "2024-02-03",
                        "activities": [
                            {
                                "time": "10:00",
                                "activity": "游览颐和园",
                                "location": "颐和园",
                                "duration": "3小时",
                                "cost": 30
                            }
                        ]
                    }
                }
            ),
            Trip(
                user_id=test_users[1].id,
                title="上海周末游",
                destination="上海",
                start_date=datetime.now() + timedelta(days=15),
                end_date=datetime.now() + timedelta(days=16),
                budget=Decimal("2000.00"),
                status="planning",
                itinerary={
                    "day1": {
                        "date": "2024-01-20",
                        "activities": [
                            {
                                "time": "10:00",
                                "activity": "外滩观光",
                                "location": "外滩",
                                "duration": "2小时",
                                "cost": 0
                            },
                            {
                                "time": "15:00",
                                "activity": "登东方明珠",
                                "location": "东方明珠塔",
                                "duration": "2小时",
                                "cost": 180
                            }
                        ]
                    },
                    "day2": {
                        "date": "2024-01-21",
                        "activities": [
                            {
                                "time": "09:00",
                                "activity": "豫园游览",
                                "location": "豫园",
                                "duration": "3小时",
                                "cost": 40
                            }
                        ]
                    }
                }
            )
        ]
        
        # 添加行程到数据库
        for trip in test_trips:
            db.add(trip)
        db.commit()
        
        # 刷新行程对象以获取ID
        for trip in test_trips:
            db.refresh(trip)
        
        # 创建测试费用记录
        test_expenses = [
            # 北京行程的费用
            Expense(
                trip_id=test_trips[0].id,
                amount=Decimal("120.00"),
                category="transport",
                description="北京地铁一日票",
                expense_date=datetime.now() + timedelta(days=30)
            ),
            Expense(
                trip_id=test_trips[0].id,
                amount=Decimal("280.00"),
                category="accommodation",
                description="酒店住宿费用",
                expense_date=datetime.now() + timedelta(days=30)
            ),
            Expense(
                trip_id=test_trips[0].id,
                amount=Decimal("150.00"),
                category="food",
                description="北京烤鸭晚餐",
                expense_date=datetime.now() + timedelta(days=30)
            ),
            
            # 上海行程的费用
            Expense(
                trip_id=test_trips[1].id,
                amount=Decimal("50.00"),
                category="transport",
                description="机场大巴",
                expense_date=datetime.now() + timedelta(days=15)
            ),
            Expense(
                trip_id=test_trips[1].id,
                amount=Decimal("180.00"),
                category="entertainment",
                description="东方明珠门票",
                expense_date=datetime.now() + timedelta(days=15)
            )
        ]
        
        # 添加费用记录到数据库
        for expense in test_expenses:
            db.add(expense)
        db.commit()
        
        print("测试数据插入完成！")
        print(f"创建了 {len(test_users)} 个测试用户")
        print(f"创建了 {len(test_trips)} 个测试行程")
        print(f"创建了 {len(test_expenses)} 条费用记录")
        
    except Exception as e:
        print(f"初始化数据库时出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()