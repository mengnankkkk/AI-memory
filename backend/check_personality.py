"""检查并修复数据库中的personality_archetype"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.core.database import async_session_maker
from app.models.companion import Companion
from sqlalchemy import select

async def check_and_fix():
    async with async_session_maker() as db:
        result = await db.execute(select(Companion))
        companions = result.scalars().all()

        print("\n当前数据库中的角色性格设置：")
        print("="*60)
        for c in companions:
            print(f"ID: {c.id} | 名字: {c.name} | 性格: {c.personality_archetype}")

        print("\n"+"="*60)
        print("开始自动修复...")

        # 修复映射
        name_to_archetype = {
            "林梓汐": "linzixi",
            "雪见": "xuejian",
            "凪": "nagi",
            "时雨": "shiyu",
            "Zoe": "zoe",
            "Kevin": "kevin"
        }

        fixed_count = 0
        for c in companions:
            if c.name in name_to_archetype:
                new_archetype = name_to_archetype[c.name]
                if c.personality_archetype != new_archetype:
                    old_value = c.personality_archetype
                    c.personality_archetype = new_archetype
                    print(f"✓ 修复 {c.name}: {old_value} → {new_archetype}")
                    fixed_count += 1

        if fixed_count > 0:
            await db.commit()
            print(f"\n✅ 修复完成！共修复 {fixed_count} 个角色")
        else:
            print("\n✅ 所有角色性格设置正确，无需修复")

if __name__ == "__main__":
    asyncio.run(check_and_fix())
