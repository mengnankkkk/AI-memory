#!/usr/bin/env python3
"""
数据库清理脚本 - 修复personality_archetype字段
"""
import sys
import os
import asyncio

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import async_session_maker
from app.models.companion import Companion
from sqlalchemy import update, select, text

async def clean_database():
    """清理数据库中的无效personality_archetype数据"""
    print("🔧 开始清理数据库...")
    
    async with async_session_maker() as db:
        # 查找所有无效的personality_archetype
        result = await db.execute(
            text("""
            SELECT id, name, personality_archetype 
            FROM companions 
            WHERE personality_archetype NOT IN ('listener', 'cheerleader', 'analyst')
            """)
        )
        
        invalid_companions = result.fetchall()
        
        if not invalid_companions:
            print("✅ 数据库中没有发现无效数据")
            return
        
        print(f"⚠️  发现 {len(invalid_companions)} 个无效的伙伴数据:")
        for companion in invalid_companions:
            print(f"  - ID: {companion[0]}, 名称: {companion[1]}, 性格: {companion[2]}")
        
        # 修复无效数据 - 将它们都设置为'listener'
        await db.execute(
            update(Companion)
            .where(Companion.personality_archetype.not_in(['listener', 'cheerleader', 'analyst']))
            .values(personality_archetype='listener')
        )
        
        await db.commit()
        print("✅ 已将所有无效的性格原型修复为'listener'")

if __name__ == "__main__":
    asyncio.run(clean_database())
