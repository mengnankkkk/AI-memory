"""
会话记忆管理器
用于管理对话上下文和短期记忆
"""
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class MemoryManager:
    """内存中的会话记忆管理（轻量级实现）"""
    
    def __init__(self, max_context_messages: int = 10):
        self.max_context_messages = max_context_messages
        self.sessions: Dict[str, Dict] = {}
        self.cleanup_interval = 3600  # 1小时清理一次过期会话
        self._cleanup_task = None
        # 不在初始化时启动任务，等到需要时再启动
    
    def _start_cleanup_task(self):
        """启动清理任务 - 只在有事件循环时调用"""
        try:
            loop = asyncio.get_running_loop()
            if self._cleanup_task is None or self._cleanup_task.done():
                self._cleanup_task = loop.create_task(self._periodic_cleanup())
        except RuntimeError:
            # 没有运行的事件循环，忽略
            pass
    
    async def _periodic_cleanup(self):
        """定期清理过期会话"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self.cleanup_expired_sessions()
            except Exception as e:
                logger.error(f"清理过期会话时出错: {e}")
    
    async def cleanup_expired_sessions(self):
        """清理过期会话"""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            last_activity = session_data.get('last_activity')
            if last_activity and now - last_activity > timedelta(hours=2):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"清理过期会话: {session_id}")
    
    async def get_session_context(self, session_id: str) -> List[Dict]:
        """获取会话上下文"""
        if session_id not in self.sessions:
            return []
        
        session_data = self.sessions[session_id]
        messages = session_data.get('messages', [])
        
        # 更新最后活动时间
        session_data['last_activity'] = datetime.now()
        
        # 返回最近的消息作为上下文
        return messages[-self.max_context_messages:]
    
    async def add_message(self, session_id: str, role: str, content: str):
        """添加消息到会话"""
        # 确保清理任务已启动
        self._start_cleanup_task()
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'messages': [],
                'created_at': datetime.now(),
                'last_activity': datetime.now()
            }
        
        session_data = self.sessions[session_id]
        session_data['messages'].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        session_data['last_activity'] = datetime.now()
        
        # 保持消息数量在合理范围内
        if len(session_data['messages']) > self.max_context_messages * 2:
            session_data['messages'] = session_data['messages'][-self.max_context_messages:]
    
    async def clear_session(self, session_id: str):
        """清空会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    async def get_session_stats(self, session_id: str) -> Optional[Dict]:
        """获取会话统计信息"""
        if session_id not in self.sessions:
            return None
        
        session_data = self.sessions[session_id]
        messages = session_data['messages']
        
        return {
            'total_messages': len(messages),
            'user_messages': len([m for m in messages if m['role'] == 'user']),
            'assistant_messages': len([m for m in messages if m['role'] == 'assistant']),
            'created_at': session_data['created_at'].isoformat(),
            'last_activity': session_data['last_activity'].isoformat()
        }

class SystemPromptGenerator:
    """系统提示词生成器"""
    
    @classmethod
    def generate_system_prompt(
        cls,
        companion_name: str,
        personality_type: str,
        custom_traits: Optional[Dict] = None
    ) -> str:
        """生成系统提示词 - 使用prompts.py中定义的角色模板"""
        from app.core.prompts import get_system_prompt
        
        # 使用prompts.py中定义的角色模板
        prompt = get_system_prompt(companion_name, personality_type)
        
        # 如果有自定义特质，添加到提示词中
        if custom_traits:
            additional_info = "\n# 额外特质\n"
            for key, value in custom_traits.items():
                additional_info += f"- {key}: {value}\n"
            prompt += additional_info
        
        return prompt

class ContentFilter:
    """内容安全过滤器"""
    
    # 基础敏感词列表
    SENSITIVE_KEYWORDS = {
        'political': ['政治', '政府', '党派', '选举'],
        'violence': ['暴力', '打击', '伤害', '攻击'],
        'adult': ['色情', '性行为', '成人内容'],
        'illegal': ['毒品', '赌博', '违法', '犯罪'],
        'personal': ['个人信息', '隐私', '身份证', '银行卡']
    }
    
    @classmethod
    async def is_content_safe(cls, content: str) -> tuple[bool, Optional[str]]:
        """
        检查内容是否安全
        
        Returns:
            (is_safe, reason) - 是否安全和不安全的原因
        """
        content_lower = content.lower()
        
        for category, keywords in cls.SENSITIVE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content_lower:
                    return False, f"包含{category}相关内容"
        
        # 检查过长的输入（防止滥用）
        if len(content) > 1000:
            return False, "输入内容过长"
        
        return True, None
    
    @classmethod  
    def get_filtered_response(cls, filter_reason: str) -> str:
        """根据过滤原因返回合适的回复"""
        responses = {
            "包含political相关内容": "我们还是聊点别的吧，比如你今天的心情怎么样？😊",
            "包含violence相关内容": "让我们聊点更温暖的话题吧～有什么开心的事想分享吗？💝", 
            "包含adult相关内容": "这个话题我不太方便讨论呢，我们聊点别的吧～😅",
            "包含illegal相关内容": "这个话题不太合适哦，我们换个话题吧！🌟",
            "输入内容过长": "你的消息有点长呢，可以简短一些告诉我吗？😊"
        }
        
        return responses.get(filter_reason, "抱歉，这个话题我不太合适回复呢 😅")

# 全局实例
memory_manager = MemoryManager()
content_filter = ContentFilter()
