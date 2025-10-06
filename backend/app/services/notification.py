"""
实时通知系统
支持WebSocket推送、邮件、短信等多种通知方式
"""
import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """统一通知服务"""
    
    def __init__(self):
        self.websocket_connections: Dict[int, List] = {}  # user_id -> [websocket]
        self.pending_notifications: Dict[int, List] = {}  # user_id -> [notifications]
    
    async def add_connection(self, user_id: int, websocket):
        """添加WebSocket连接"""
        if user_id not in self.websocket_connections:
            self.websocket_connections[user_id] = []
        self.websocket_connections[user_id].append(websocket)
        
        # 发送未读通知
        await self._send_pending_notifications(user_id)
    
    async def remove_connection(self, user_id: int, websocket):
        """移除WebSocket连接"""
        if user_id in self.websocket_connections:
            try:
                self.websocket_connections[user_id].remove(websocket)
                if not self.websocket_connections[user_id]:
                    del self.websocket_connections[user_id]
            except ValueError:
                pass
    
    async def send_notification(
        self, 
        user_id: int, 
        notification_type: str,
        title: str,
        content: str,
        data: Optional[Dict] = None
    ):
        """发送通知"""
        notification = {
            "type": notification_type,
            "title": title,
            "content": content,
            "data": data or {},
            "timestamp": datetime.now().isoformat(),
            "id": f"{user_id}_{datetime.now().timestamp()}"
        }
        
        # 尝试实时推送
        if user_id in self.websocket_connections:
            disconnected = []
            for ws in self.websocket_connections[user_id]:
                try:
                    await ws.send_text(json.dumps({
                        "type": "notification",
                        "payload": notification
                    }))
                except Exception as e:
                    logger.error(f"WebSocket发送失败: {e}")
                    disconnected.append(ws)
            
            # 清理失效连接
            for ws in disconnected:
                await self.remove_connection(user_id, ws)
        
        # 如果没有活跃连接，存储为待发送
        if user_id not in self.websocket_connections:
            if user_id not in self.pending_notifications:
                self.pending_notifications[user_id] = []
            self.pending_notifications[user_id].append(notification)
            
            # 限制未读通知数量
            if len(self.pending_notifications[user_id]) > 50:
                self.pending_notifications[user_id] = self.pending_notifications[user_id][-50:]
    
    async def _send_pending_notifications(self, user_id: int):
        """发送待处理的通知"""
        if user_id in self.pending_notifications:
            for notification in self.pending_notifications[user_id]:
                if user_id in self.websocket_connections:
                    for ws in self.websocket_connections[user_id]:
                        try:
                            await ws.send_text(json.dumps({
                                "type": "notification",
                                "payload": notification
                            }))
                        except Exception:
                            pass
            
            # 清空已发送的通知
            del self.pending_notifications[user_id]
    
    async def send_companion_update(self, user_id: int, companion_id: int, update_type: str):
        """发送伙伴更新通知"""
        await self.send_notification(
            user_id,
            "companion_update",
            "伙伴更新",
            f"您的AI伙伴已{update_type}",
            {"companion_id": companion_id, "update_type": update_type}
        )
    
    async def send_chat_quality_alert(self, user_id: int, companion_id: int, score: float):
        """发送对话质量警报"""
        if score < 3.0:  # 低质量警报
            await self.send_notification(
                user_id,
                "quality_alert",
                "对话质量提醒",
                f"最近的对话质量较低(评分:{score:.1f})，建议调整伙伴设置",
                {"companion_id": companion_id, "score": score}
            )
    
    async def send_system_maintenance(self, message: str):
        """发送系统维护通知给所有用户"""
        tasks = []
        for user_id in self.websocket_connections.keys():
            task = self.send_notification(
                user_id,
                "system_maintenance",
                "系统维护通知",
                message
            )
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_prompt_experiment_result(
        self, 
        user_id: int, 
        companion_id: int, 
        old_version: str, 
        new_version: str,
        improvement: float
    ):
        """发送Prompt实验结果通知"""
        if improvement > 0.1:  # 显著改善
            await self.send_notification(
                user_id,
                "experiment_result",
                "Prompt优化成功",
                f"新版本Prompt效果提升{improvement:.1%}，已自动应用",
                {
                    "companion_id": companion_id,
                    "old_version": old_version,
                    "new_version": new_version,
                    "improvement": improvement
                }
            )
    
    async def get_unread_notifications(self, user_id: int):
        """获取用户未读通知"""
        return self.pending_notifications.get(user_id, [])
    
    def get_connection_count(self) -> int:
        """获取当前连接数"""
        return sum(len(connections) for connections in self.websocket_connections.values())
    
    def get_pending_count(self, user_id: int) -> int:
        """获取用户未读通知数"""
        return len(self.pending_notifications.get(user_id, []))

# 全局通知服务实例
notification_service = NotificationService()
