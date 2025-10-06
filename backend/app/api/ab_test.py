"""
A/B测试管理API
提供Prompt版本管理、切换、效果分析等功能
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.companion import Companion
from app.services.analytics import analytics_service
from app.core.prompts import PROMPT_VERSION_MAP
from typing import Dict, List

router = APIRouter(prefix="/ab-test", tags=["ab-test"])

@router.get("/prompt-versions")
async def get_prompt_versions():
    """获取所有可用的Prompt版本"""
    return {
        "versions": list(PROMPT_VERSION_MAP.keys()),
        "current_default": "v1"
    }

@router.post("/switch-prompt/{companion_id}")
async def switch_prompt_version(
    companion_id: int,
    version: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """切换伙伴的Prompt版本"""
    if version not in PROMPT_VERSION_MAP:
        raise HTTPException(status_code=400, detail="无效的Prompt版本")
    
    result = await db.execute(select(Companion).where(Companion.id == companion_id))
    companion = result.scalar_one_or_none()
    if not companion:
        raise HTTPException(status_code=404, detail="伙伴不存在")
    
    # 更新Prompt版本
    companion.prompt_version = version
    await db.commit()
    
    # 埋点记录版本切换
    await analytics_service.track_user_behavior(
        companion.user_id, 
        "prompt_version_switch",
        companion_id=companion_id,
        old_version=getattr(companion, 'prompt_version', 'v1'),
        new_version=version
    )
    
    return {"message": f"Prompt版本已切换为 {version}"}

@router.get("/stats/{version}")
async def get_prompt_stats(version: str, days: int = 7):
    """获取指定Prompt版本的统计数据"""
    if version not in PROMPT_VERSION_MAP:
        raise HTTPException(status_code=400, detail="无效的Prompt版本")
    
    stats = await analytics_service.get_prompt_stats(version, days)
    return {
        "version": version,
        "days": days,
        "stats": stats
    }

@router.get("/compare")
async def compare_prompt_versions(
    version1: str = "v1",
    version2: str = "v2", 
    days: int = 7
):
    """对比两个Prompt版本的效果"""
    if version1 not in PROMPT_VERSION_MAP or version2 not in PROMPT_VERSION_MAP:
        raise HTTPException(status_code=400, detail="无效的Prompt版本")
    
    stats1 = await analytics_service.get_prompt_stats(version1, days)
    stats2 = await analytics_service.get_prompt_stats(version2, days)
    
    # 计算平均质量得分
    def calc_avg_quality(stats):
        total_score = 0
        total_feedback = 0
        for date_stats in stats.get("quality", {}).values():
            if isinstance(date_stats, dict):
                total_score += date_stats.get("avg_score", 0) * date_stats.get("feedback_count", 0)
                total_feedback += date_stats.get("feedback_count", 0)
        return total_score / total_feedback if total_feedback > 0 else 0
    
    avg_quality1 = calc_avg_quality(stats1)
    avg_quality2 = calc_avg_quality(stats2)
    
    # 计算总使用量
    total_usage1 = sum(stats1.get("usage", {}).values())
    total_usage2 = sum(stats2.get("usage", {}).values())
    
    return {
        "comparison": {
            version1: {
                "avg_quality_score": avg_quality1,
                "total_usage": total_usage1,
                "stats": stats1
            },
            version2: {
                "avg_quality_score": avg_quality2,
                "total_usage": total_usage2,
                "stats": stats2
            }
        },
        "winner": {
            "by_quality": version1 if avg_quality1 > avg_quality2 else version2,
            "by_usage": version1 if total_usage1 > total_usage2 else version2
        }
    }

@router.post("/auto-assign/{companion_id}")
async def auto_assign_ab_test(
    companion_id: int,
    db: AsyncSession = Depends(get_db)
):
    """自动为伙伴分配A/B测试版本"""
    result = await db.execute(select(Companion).where(Companion.id == companion_id))
    companion = result.scalar_one_or_none()
    if not companion:
        raise HTTPException(status_code=404, detail="伙伴不存在")
    
    # 简单的A/B分配逻辑：根据伙伴ID奇偶性分配
    assigned_version = "v2" if companion_id % 2 == 0 else "v1"
    
    companion.prompt_version = assigned_version
    await db.commit()
    
    # 埋点记录自动分配
    await analytics_service.track_user_behavior(
        companion.user_id,
        "ab_test_auto_assign",
        companion_id=companion_id,
        assigned_version=assigned_version
    )
    
    return {
        "message": "已自动分配A/B测试版本",
        "assigned_version": assigned_version
    }
