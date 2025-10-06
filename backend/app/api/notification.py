"""
通知API
提供系统通知推送、未读通知查询等
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
from app.services.notification import notification_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notification", tags=["notification"])

@router.post("/send")
async def send_notification(
    user_id: int = Body(...),
    notification_type: str = Body(...),
    title: str = Body(...),
    content: str = Body(...),
    data: Optional[Dict] = Body(None)
):
    """发送通知"""
    try:
        await notification_service.send_notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            content=content,
            data=data
        )
        return {"success": True}
    except Exception as e:
        logger.error(f"发送通知失败: {e}")
        raise HTTPException(status_code=500, detail="发送通知失败")

@router.get("/unread/{user_id}")
async def get_unread_notifications(user_id: int):
    """获取用户未读通知"""
    try:
        unread = []
        if hasattr(notification_service, "get_unread_notifications"):
            unread = await notification_service.get_unread_notifications(user_id)
        return {"unread": unread}
    except Exception as e:
        logger.error(f"获取未读通知失败: {e}")
        raise HTTPException(status_code=500, detail="获取未读通知失败")
