"""
离线生活API端点
提供离线生活日志的查询和管理功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_maker
from app.models.event import OfflineLifeLog

async def get_async_session():
    """获取异步数据库会话"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
from app.services.personal_timeline_simulator import timeline_simulator
from app.services.timeline_scheduler import timeline_scheduler
from app.api.dependencies import get_current_user
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/offline-life", tags=["离线生活"])


@router.get("/logs/{companion_id}")
async def get_offline_logs(
    companion_id: str,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    log_type: Optional[str] = Query(None),
    min_importance: int = Query(0, ge=0, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """获取伙伴的离线生活日志"""
    try:
        query = db.query(OfflineLifeLog).filter(
            OfflineLifeLog.companion_id == companion_id
        )
        
        if log_type:
            query = query.filter(OfflineLifeLog.log_type == log_type)
        
        if min_importance > 0:
            query = query.filter(OfflineLifeLog.importance_score >= min_importance)
        
        logs = await query.order_by(
            OfflineLifeLog.generated_at.desc()
        ).offset(offset).limit(limit).all()
        
        return {
            "logs": [
                {
                    "id": log.id,
                    "content": log.log_content,
                    "type": log.log_type,
                    "importance_score": log.importance_score,
                    "emotion": log.associated_emotion,
                    "is_shared": log.is_shared_with_user,
                    "generated_at": log.generated_at.isoformat(),
                    "shared_at": log.shared_at.isoformat() if log.shared_at else None
                }
                for log in logs
            ],
            "total": len(logs)
        }
        
    except Exception as e:
        logger.error(f"获取离线日志失败: {e}")
        raise HTTPException(status_code=500, detail="获取离线日志失败")


@router.get("/important-logs/{companion_id}")
async def get_important_logs(
    companion_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取需要主动提及的重要日志"""
    try:
        logs = await timeline_simulator.get_important_logs_for_user(
            companion_id, str(current_user.id)
        )
        
        return {
            "logs": [
                {
                    "id": log.id,
                    "content": log.log_content,
                    "type": log.log_type,
                    "importance_score": log.importance_score,
                    "emotion": log.associated_emotion,
                    "generated_at": log.generated_at.isoformat()
                }
                for log in logs
            ],
            "count": len(logs)
        }
        
    except Exception as e:
        logger.error(f"获取重要日志失败: {e}")
        raise HTTPException(status_code=500, detail="获取重要日志失败")


@router.post("/generate/{companion_id}")
async def generate_offline_logs(
    companion_id: str,
    hours_offline: int = Query(24, ge=1, le=168),  # 1小时到1周
    current_user: User = Depends(get_current_user)
):
    """手动为伙伴生成离线生活日志"""
    try:
        logs = await timeline_simulator.generate_offline_life_logs(
            companion_id, hours_offline
        )
        
        return {
            "message": f"成功生成 {len(logs)} 条离线生活日志",
            "logs_count": len(logs),
            "hours_offline": hours_offline
        }
        
    except Exception as e:
        logger.error(f"生成离线日志失败: {e}")
        raise HTTPException(status_code=500, detail="生成离线日志失败")


@router.post("/simulate-all")
async def simulate_all_companions(
    current_user: User = Depends(get_current_user)
):
    """为所有伙伴模拟离线生活（管理员功能）"""
    try:
        await timeline_simulator.simulate_offline_life_for_all_companions()
        
        return {
            "message": "成功为所有伙伴生成离线生活日志"
        }
        
    except Exception as e:
        logger.error(f"批量生成离线日志失败: {e}")
        raise HTTPException(status_code=500, detail="批量生成离线日志失败")


@router.post("/scheduler/start")
async def start_scheduler(
    current_user: User = Depends(get_current_user)
):
    """启动时间线调度器"""
    try:
        await timeline_scheduler.start()
        
        return {
            "message": "时间线调度器已启动",
            "interval_hours": timeline_scheduler.interval_hours
        }
        
    except Exception as e:
        logger.error(f"启动调度器失败: {e}")
        raise HTTPException(status_code=500, detail="启动调度器失败")


@router.post("/scheduler/stop")
async def stop_scheduler(
    current_user: User = Depends(get_current_user)
):
    """停止时间线调度器"""
    try:
        await timeline_scheduler.stop()
        
        return {
            "message": "时间线调度器已停止"
        }
        
    except Exception as e:
        logger.error(f"停止调度器失败: {e}")
        raise HTTPException(status_code=500, detail="停止调度器失败")


@router.post("/scheduler/trigger")
async def trigger_simulation(
    current_user: User = Depends(get_current_user)
):
    """立即触发一次离线生活模拟"""
    try:
        await timeline_scheduler.trigger_immediate_simulation()
        
        return {
            "message": "离线生活模拟已触发"
        }
        
    except Exception as e:
        logger.error(f"触发模拟失败: {e}")
        raise HTTPException(status_code=500, detail="触发模拟失败")


@router.get("/scheduler/status")
async def get_scheduler_status(
    current_user: User = Depends(get_current_user)
):
    """获取调度器状态"""
    return {
        "is_running": timeline_scheduler.is_running,
        "interval_hours": timeline_scheduler.interval_hours
    }


@router.put("/scheduler/interval")
async def set_scheduler_interval(
    hours: int = Query(..., ge=1, le=168),  # 1小时到1周
    current_user: User = Depends(get_current_user)
):
    """设置调度器执行间隔"""
    try:
        timeline_scheduler.set_interval(hours)
        
        return {
            "message": f"调度器间隔已设置为 {hours} 小时",
            "interval_hours": hours
        }
        
    except Exception as e:
        logger.error(f"设置调度器间隔失败: {e}")
        raise HTTPException(status_code=500, detail="设置调度器间隔失败")
