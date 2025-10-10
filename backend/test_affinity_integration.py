#!/usr/bin/env python3
"""
好感度系统集成测试脚本
测试自动化好感度分析和数据库更新功能
"""
import asyncio
import logging
from app.services.affinity_engine import analyze_and_update_affinity, affinity_engine

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_affinity_integration():
    """测试好感度系统集成"""
    print("🚀 开始测试好感度系统集成...")
    
    # 测试用例
    test_cases = [
        {
            "user_id": "test_user_001",
            "companion_id": 1,
            "message": "谢谢你的帮助！",
            "personality_type": "linzixi",
            "expected_emotion": "positive"
        },
        {
            "user_id": "test_user_001", 
            "companion_id": 1,
            "message": "我今天心情不太好...",
            "personality_type": "linzixi",
            "expected_emotion": "negative"
        },
        {
            "user_id": "test_user_001",
            "companion_id": 1, 
            "message": "你好，初次见面",
            "personality_type": "linzixi",
            "expected_emotion": "neutral"
        },
        {
            "user_id": "test_user_001",
            "companion_id": 1,
            "message": "我觉得你很特别，想了解你更多",
            "personality_type": "linzixi", 
            "expected_emotion": "romantic"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 测试用例 {i}: {test_case['message'][:20]}...")
        
        try:
            # 调用便捷接口
            result = await analyze_and_update_affinity(
                user_id=test_case["user_id"],
                companion_id=test_case["companion_id"],
                message=test_case["message"],
                personality_type=test_case["personality_type"],
                interaction_type="test"
            )
            
            # 输出结果
            if result["success"]:
                print(f"✅ 分析成功:")
                print(f"   - 情感: {result['emotion']} (强度: {result['emotion_intensity']:.2f})")
                print(f"   - 好感度变化: {result['affinity_change']:+d}")
                print(f"   - 新好感度: {result['new_affinity_score']}")
                print(f"   - 等级: {result['new_level']}")
                print(f"   - 等级变化: {result['level_changed']}")
                print(f"   - 值得记忆: {result['is_memorable']}")
                
                # 验证期望
                if result['emotion'] == test_case['expected_emotion']:
                    print(f"✅ 情感识别正确!")
                else:
                    print(f"⚠️ 情感识别不符合期望 (期望: {test_case['expected_emotion']})")
            else:
                print(f"❌ 分析失败: {result['error']}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    print(f"\n🎉 好感度系统集成测试完成!")


async def test_direct_engine():
    """测试引擎核心功能"""
    print("\n🔧 测试引擎核心功能...")
    
    try:
        # 直接测试引擎
        result = await affinity_engine.process_user_message(
            user_message="你今天看起来很漂亮！",
            current_affinity_score=100,
            current_trust_score=50,
            current_tension_score=10,
            current_level="friend",
            current_mood="happy",
            companion_name="林子希",
            user_id="test_user_002",
            companion_id=2
        )
        
        print(f"✅ 引擎测试成功:")
        print(f"   - 主要情感: {result.emotion_analysis.primary_emotion}")
        print(f"   - 用户意图: {result.emotion_analysis.user_intent}")
        print(f"   - 好感度变化: {result.affinity_change:+d}")
        print(f"   - 新等级: {result.new_level_name}")
        print(f"   - 保护警告: {result.protection_warnings}")
        
    except Exception as e:
        print(f"❌ 引擎测试失败: {e}")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_affinity_integration())
    asyncio.run(test_direct_engine())
