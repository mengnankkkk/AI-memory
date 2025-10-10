"""
初始化6个系统伙伴的好感度数据
为每个伙伴设置不同的初始状态
"""
import asyncio
import random
import json
from datetime import datetime, timedelta
from app.services.redis_utils import redis_affinity_manager

# 6个系统伙伴的初始数据配置
COMPANION_INITIAL_DATA = [
    {
        "companion_id": 1,
        "name": "林梓汐",
        "affinity_score": 80,  # 陌生阶段 (0-100)
        "trust_score": 15,
        "tension_score": 5,
        "romance_level": "stranger",
        "current_mood": "专注",
        "total_interactions": 3,
        "positive_interactions": 2,
        "negative_interactions": 0,
        "days_since_first_meet": 2,
        "gifts_received": 0,
        "special_moments": 1
    },
    {
        "companion_id": 2,
        "name": "雪见",
        "affinity_score": 120,  # 认识阶段 (101-250)
        "trust_score": 25,
        "tension_score": 3,
        "romance_level": "acquaintance",
        "current_mood": "警觉",
        "total_interactions": 8,
        "positive_interactions": 6,
        "negative_interactions": 1,
        "days_since_first_meet": 5,
        "gifts_received": 1,
        "special_moments": 2
    },
    {
        "companion_id": 3,
        "name": "凪",
        "affinity_score": 180,  # 认识阶段
        "trust_score": 30,
        "tension_score": 2,
        "romance_level": "acquaintance",
        "current_mood": "开心",
        "total_interactions": 12,
        "positive_interactions": 10,
        "negative_interactions": 0,
        "days_since_first_meet": 7,
        "gifts_received": 2,
        "special_moments": 3
    },
    {
        "companion_id": 4,
        "name": "时雨",
        "affinity_score": 95,  # 陌生阶段
        "trust_score": 20,
        "tension_score": 8,
        "romance_level": "stranger",
        "current_mood": "沉思",
        "total_interactions": 5,
        "positive_interactions": 3,
        "negative_interactions": 1,
        "days_since_first_meet": 3,
        "gifts_received": 0,
        "special_moments": 1
    },
    {
        "companion_id": 5,
        "name": "Zoe",
        "affinity_score": 220,  # 认识阶段
        "trust_score": 35,
        "tension_score": 0,
        "romance_level": "acquaintance",
        "current_mood": "兴奋",
        "total_interactions": 15,
        "positive_interactions": 13,
        "negative_interactions": 0,
        "days_since_first_meet": 9,
        "gifts_received": 3,
        "special_moments": 4
    },
    {
        "companion_id": 6,
        "name": "凯文",
        "affinity_score": 150,  # 认识阶段
        "trust_score": 28,
        "tension_score": 1,
        "romance_level": "acquaintance",
        "current_mood": "轻松",
        "total_interactions": 10,
        "positive_interactions": 8,
        "negative_interactions": 1,
        "days_since_first_meet": 6,
        "gifts_received": 1,
        "special_moments": 2
    }
]


async def init_companion_data_for_user(user_id: str):
    """
    为指定用户初始化所有伙伴的数据

    Args:
        user_id: 用户ID
    """
    print(f"\n{'='*60}")
    print(f"为用户 {user_id} 初始化伙伴数据")
    print(f"{'='*60}\n")

    for companion_data in COMPANION_INITIAL_DATA:
        companion_id = companion_data["companion_id"]
        companion_name = companion_data["name"]

        try:
            # 构建完整的状态数据
            state_data = {
                "user_id": user_id,
                "companion_id": companion_id,
                "affinity_score": companion_data["affinity_score"],
                "trust_score": companion_data["trust_score"],
                "tension_score": companion_data["tension_score"],
                "romance_level": companion_data["romance_level"],
                "current_mood": companion_data["current_mood"],
                "total_interactions": companion_data["total_interactions"],
                "positive_interactions": companion_data["positive_interactions"],
                "negative_interactions": companion_data["negative_interactions"],
                "days_since_first_meet": companion_data["days_since_first_meet"],
                "gifts_received": companion_data["gifts_received"],
                "special_moments": companion_data["special_moments"],
                "last_interaction_at": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat()
            }

            # 使用Redis管理器初始化状态
            state = await redis_affinity_manager.initialize_companion_state(
                user_id=user_id,
                companion_id=companion_id,
                initial_affinity=companion_data["affinity_score"],
                initial_trust=companion_data["trust_score"],
                initial_tension=companion_data["tension_score"],
                romance_level=companion_data["romance_level"]
            )

            if not state:
                print(f"❌ {companion_name} 初始化失败")
                continue

            # 更新额外字段
            from app.core.redis_client import get_redis
            redis_client = await get_redis()

            state_key = f"companion_state:{user_id}:{companion_id}"

            # 读取当前状态并更新
            state_json = await redis_client.get(state_key)
            if state_json:
                state = json.loads(state_json)
                state.update({
                    "current_mood": companion_data["current_mood"],
                    "total_interactions": companion_data["total_interactions"],
                    "positive_interactions": companion_data["positive_interactions"],
                    "negative_interactions": companion_data["negative_interactions"],
                    "days_since_first_meet": companion_data["days_since_first_meet"],
                    "gifts_received": companion_data["gifts_received"],
                    "special_moments": companion_data["special_moments"],
                })

                # 保存回Redis
                await redis_client.setex(
                    state_key,
                    30 * 24 * 3600,  # 30天
                    json.dumps(state)
                )

            print(f"[OK] {companion_name} (ID:{companion_id})")
            print(f"   好感度: {companion_data['affinity_score']} | 等级: {companion_data['romance_level']}")
            print(f"   交流: {companion_data['total_interactions']}次 | 相识: {companion_data['days_since_first_meet']}天")
            print(f"   心情: {companion_data['current_mood']} | 礼物: {companion_data['gifts_received']}个")
            print()

        except Exception as e:
            print(f"[ERROR] {companion_name} 初始化失败: {e}")
            continue

    print(f"{'='*60}")
    print(f"[SUCCESS] 所有伙伴数据初始化完成！")
    print(f"{'='*60}\n")


async def main():
    """主函数"""
    import sys

    # 获取用户ID（从命令行参数或使用默认值）
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
    else:
        # 使用默认测试用户ID
        user_id = "2"  # 假设测试用户ID为2
        print(f"[INFO] 未指定用户ID，使用默认测试用户: {user_id}")

    await init_companion_data_for_user(user_id)

    # 验证数据
    print("\n" + "="*60)
    print("验证数据...")
    print("="*60 + "\n")

    for companion_data in COMPANION_INITIAL_DATA:
        companion_id = companion_data["companion_id"]
        state = await redis_affinity_manager.get_companion_state(user_id, companion_id)

        if state:
            print(f"[V] {companion_data['name']}: 好感度={state.get('affinity_score')}, "
                  f"等级={state.get('romance_level')}, "
                  f"交流={state.get('total_interactions')}次")
        else:
            print(f"[X] {companion_data['name']}: 数据获取失败")


if __name__ == "__main__":
    asyncio.run(main())
