"""
AI服务功能测试
直接测试通义千问API调用，输出原始响应
"""

import os
import sys
from datetime import datetime

# 添加项目路径到sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import AIService

def test_ai_service():
    """测试AI服务功能"""
    print("=" * 60)
    print("开始测试AI服务功能")
    print("=" * 60)
    
    # 创建AI服务实例
    ai_service = AIService()
    
    # 检查API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 错误：未找到DASHSCOPE_API_KEY环境变量")
        print("请在.env文件中设置DASHSCOPE_API_KEY")
        return
    
    print(f"✅ API密钥已配置: {api_key[:10]}...")
    print(f"✅ 模型: {ai_service.model}")
    print(f"✅ 基础URL: {ai_service.client.base_url}")
    print()
    
    # 测试参数
    test_params = {
        "destination": "北京",
        "start_date": "2024-12-01",
        "end_date": "2024-12-03",
        "budget": 3000.0,
        "preferences": "喜欢历史文化景点，不喜欢太累的行程",
        "travel_style": "文化"
    }
    
    print("测试参数:")
    for key, value in test_params.items():
        print(f"  {key}: {value}")
    print()
    
    print("正在调用AI服务...")
    print("-" * 60)
    
    try:
        # 调用AI服务
        result = ai_service.generate_itinerary(**test_params)
        
        print("AI服务调用结果:")
        print(f"成功状态: {result.get('success')}")
        print(f"消息: {result.get('message')}")
        print()
        
        if result.get('success'):
            print("✅ AI调用成功!")
            print()
            print("生成的行程数据:")
            print("-" * 40)
            
            # 输出格式化的行程数据
            data = result.get('data')
            if data:
                for day_key, day_data in data.items():
                    print(f"\n📅 {day_key.upper()} - {day_data.get('date', 'N/A')}")
                    activities = day_data.get('activities', [])
                    for i, activity in enumerate(activities, 1):
                        print(f"  {i}. {activity.get('time', 'N/A')} - {activity.get('activity', 'N/A')}")
                        print(f"     📍 地点: {activity.get('location', 'N/A')}")
                        print(f"     ⏱️ 时长: {activity.get('duration', 'N/A')}")
                        print(f"     💰 费用: {activity.get('cost', 'N/A')}元")
                        print(f"     🏷️ 类型: {activity.get('type', 'N/A')}")
                        print(f"     📝 描述: {activity.get('description', 'N/A')}")
                        print()
            else:
                print("⚠️ 警告：返回的数据为空")
        else:
            print("❌ AI调用失败!")
            print(f"错误信息: {result.get('message')}")
            
            # 如果有原始响应，也输出
            if 'raw_response' in result:
                print("\n原始AI响应:")
                print("-" * 40)
                print(result['raw_response'])
                
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("AI服务测试完成")
    print("=" * 60)

def test_ai_raw_call():
    """测试AI原始调用，输出完全未处理的响应"""
    print("\n" + "=" * 60)
    print("测试AI原始调用")
    print("=" * 60)
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # 简单的测试提示
        test_prompt = """
请为我制定一个简单的北京2天旅行行程。

要求：
1. 第一天：天安门广场、故宫
2. 第二天：长城、颐和园
3. 请用JSON格式返回，包含每天的活动安排

只返回JSON，不要其他文字。
"""
        
        print("发送给AI的提示词:")
        print("-" * 40)
        print(test_prompt)
        print("-" * 40)
        
        print("\n正在调用AI...")
        
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "你是一个专业的旅行规划师。"},
                {"role": "user", "content": test_prompt}
            ],
            temperature=0
        )
        
        print("\n✅ AI原始响应:")
        print("=" * 60)
        print(completion.choices[0].message.content)
        print("=" * 60)
        
        print(f"\n📊 响应统计:")
        print(f"模型: {completion.model}")
        print(f"使用的tokens: {completion.usage.total_tokens if completion.usage else 'N/A'}")
        
    except Exception as e:
        print(f"❌ 原始调用失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🤖 AI服务测试程序")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行测试
    test_ai_service()
    test_ai_raw_call()