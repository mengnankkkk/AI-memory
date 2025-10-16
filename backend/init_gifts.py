# -*- coding: utf-8 -*-
"""
初始化用户礼物库存
为用户创建初始礼物库存
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import init_db, async_session_maker
from app.models.gift import UserGiftInventory
from app.core.gift_config import get_all_gifts
from sqlalchemy import select
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_gifts")


async def init_user_gift_inventory(user_id: str = "2"):
    """为用户初始化礼物库存"""
    async with async_session_maker() as session:
        gifts = get_all_gifts()
        created_count = 0
        updated_count = 0

        for gift_config in gifts:
            # 检查用户是否已有该礼物
            stmt = select(UserGiftInventory).where(
                UserGiftInventory.user_id == user_id,
                UserGiftInventory.gift_id == gift_config["gift_id"]
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if not existing:
                # 创建新库存
                inventory = UserGiftInventory(
                    user_id=user_id,
                    gift_id=gift_config["gift_id"],
                    quantity=gift_config["initial_quantity"],
                    max_quantity=gift_config["max_quantity"]
                )
                session.add(inventory)
                created_count += 1
                logger.info(f"[创建] {gift_config['name']}: {gift_config['initial_quantity']}个")
            else:
                # 更新现有库存（可选：只更新max_quantity）
                existing.max_quantity = gift_config["max_quantity"]
                updated_count += 1
                logger.info(f"[更新] {gift_config['name']}: 当前{existing.quantity}个")

        await session.commit()
        logger.info(f"\n礼物库存初始化完成: 新创建 {created_count} 个，更新 {updated_count} 个")


async def main():
    """主函数"""
    print("=" * 60)
    print("礼物系统初始化脚本")
    print("=" * 60)
    print()

    # 1. 初始化数据库
    print("[1/2] 初始化数据库连接...")
    try:
        await init_db()
        print("[成功] 数据库连接成功")
    except Exception as e:
        print(f"[失败] 数据库连接失败: {e}")
        return

    # 2. 初始化礼物库存
    print("\n[2/2] 初始化礼物库存...")
    try:
        # 默认为用户ID=2初始化，也可以传参
        user_id = sys.argv[1] if len(sys.argv) > 1 else "2"
        await init_user_gift_inventory(user_id)
        print("[成功] 礼物库存初始化完成")
    except Exception as e:
        print(f"[失败] 礼物库存初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return

    print()
    print("=" * 60)
    print("[完成] 礼物系统初始化成功！")
    print("=" * 60)
    print()
    print("现在可以：")
    print("1. 启动后端服务测试礼物赠送功能")
    print("2. 查看用户的礼物库存")
    print()


if __name__ == "__main__":
    asyncio.run(main())
