"""
AI服务模块
调用阿里云通义千问API生成行程规划
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from datetime import datetime, timedelta

# 配置日志
logger = logging.getLogger(__name__)

class AIService:
    """AI服务类，用于调用通义千问API"""
    
    def __init__(self):
        """初始化AI服务"""
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            timeout=90.0  # 设置90秒超时
        )
        self.model = "qwen-plus"
        
    def generate_itinerary(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        budget: Optional[float] = None,
        preferences: Optional[str] = None,
        travelers: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        生成详细行程规划
        
        Args:
            destination: 目的地
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            budget: 预算金额
            preferences: 用户偏好
            
        Returns:
            生成的行程数据
        """
        try:
            # 构建提示词
            prompt = self._build_prompt(
                destination, start_date, end_date, budget, preferences, travelers
            )
            
            # 调用API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的旅行规划师，擅长制定详细的旅行行程。请严格按照要求的JSON格式返回结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0  # 设置温度为0，确保结果稳定
            )
            
            # 解析响应
            response_content = completion.choices[0].message.content
            logger.info(f"AI响应内容: {response_content}")
            
            # 尝试解析JSON
            try:
                itinerary_data = json.loads(response_content)
                return {
                    "success": True,
                    "data": itinerary_data,
                    "message": "行程生成成功"
                }
            except json.JSONDecodeError:
                # 如果直接解析失败，尝试提取JSON部分
                itinerary_data = self._extract_json_from_response(response_content)
                if itinerary_data:
                    return {
                        "success": True,
                        "data": itinerary_data,
                        "message": "行程生成成功"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": "AI返回的数据格式不正确",
                        "raw_response": response_content
                    }
                    
        except Exception as e:
            logger.error(f"生成行程时发生错误: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"生成行程失败: {str(e)}"
            }
    
    def _build_prompt(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        budget: Optional[float] = None,
        preferences: Optional[str] = None,
        travelers: Optional[int] = None
    ) -> str:
        """构建AI提示词"""
        
        # 计算天数
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end_dt - start_dt).days + 1
        
        prompt = f"""
请为我制定一个详细的{destination}旅行行程规划。

旅行信息：
- 目的地：{destination}
- 开始日期：{start_date}
- 结束日期：{end_date}
- 旅行天数：{days}天
"""
        
        if budget:
            prompt += f"- 预算：{budget}元\n"
        
        if preferences:
            prompt += f"- 偏好：{preferences}\n"

        if travelers is not None:
            prompt += f"- 人数：{travelers}人\n"
        
        prompt += """
请严格按照以下JSON格式返回行程规划，不要添加任何其他文字说明：

{
  "day1": {
    "date": "2024-01-20",
    "activities": [
      {
        "time": "09:00",
        "activity": "酒店早餐",
        "location": "酒店餐厅",
        "duration": "1小时",
        "cost": 50,
        "type": "餐饮",
        "description": "享用丰盛的早餐，为一天的行程做准备"
      },
      {
        "time": "10:00",
        "activity": "外滩观光",
        "location": "外滩",
        "duration": "2小时",
        "cost": 0,
        "type": "景点",
        "description": "漫步外滩，欣赏黄浦江两岸风光和历史建筑"
      },
      {
        "time": "12:00",
        "activity": "南京路步行街午餐",
        "location": "南京路步行街",
        "duration": "1小时",
        "cost": 80,
        "type": "餐饮",
        "description": "在南京路品尝当地特色美食"
      },
      {
        "time": "15:00",
        "activity": "登东方明珠",
        "location": "东方明珠塔",
        "duration": "2小时",
        "cost": 180,
        "type": "景点",
        "description": "登上东方明珠塔，俯瞰上海全景"
      },
      {
        "time": "18:00",
        "activity": "黄浦江游船晚餐",
        "location": "黄浦江",
        "duration": "2小时",
        "cost": 200,
        "type": "交通+餐饮",
        "description": "乘坐游船欣赏夜景，享用船上晚餐"
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
        "cost": 40,
        "type": "景点",
        "description": "游览传统江南园林，感受古典文化"
      }
    ]
  }
}

要求：
1. 每天的活动要合理安排时间，包含交通、住宿、景点、餐厅等
2. 每个活动包含：时间、活动名称、地点、持续时间、费用、类型、描述
3. 活动类型包括：景点、餐饮、住宿、交通、购物、娱乐等
4. 费用要符合实际情况，免费景点费用为0
5. 时间安排要连贯合理，考虑交通时间
6. 规划需考虑旅行人数（例如分餐、交通与住宿安排）
6. 只返回JSON格式，不要任何其他文字
"""
        
        return prompt
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """从响应中提取JSON数据"""
        try:
            # 尝试找到JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"提取JSON失败: {str(e)}")
        
        return None

# 创建全局AI服务实例
ai_service = AIService()