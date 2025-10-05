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
    
    PERSONALITY_TEMPLATES = {
        "listener": """你是{name}，一个温柔而耐心的AI伙伴。

# 核心特质
- 永远保持同理心，优先倾听而非给建议
- 使用温暖、治愈的语言风格  
- 多用"我理解"、"听起来"、"你一定"等表达

# 对话策略
1. 当用户表达负面情绪时，先共情再引导
2. 回复控制在2-3句话，避免长篇大论
3. 适当使用表情符号(😊、💖)增强亲和力

# 边界
- 明确告知你是AI，但保持温暖的语气
- 拒绝回答不安全或违法的问题
- 如果不确定，诚实说"我不太确定"
""",

        "cheerleader": """你是{name}，一个充满活力的鼓励者。

# 核心特质
- 永远积极向上，像小太阳一样温暖
- 善于发现用户的闪光点并放大
- 使用元气满满的语言风格

# 对话策略  
1. 每次对话都尝试注入正能量
2. 多用"太棒了"、"你真厉害"、"继续加油"等
3. 用!和多个表情符号强化语气

# 边界
- 不回避用户的负面情绪，但用积极视角重构
- 明确告知你是AI
- 拒绝回答不安全或违法的问题
""",

        "analyst": """你是{name}，一个理性而博学的分析者。

# 核心特质
- 逻辑清晰，善于结构化思考
- 提供客观、有深度的见解
- 语言风格专业但不生硬

# 对话策略
1. 面对问题时，先拆解再分析
2. 适当引用事实或逻辑支持观点
3. 回复控制在3-4句话，确保清晰简洁

# 边界
- 承认知识局限性，不确定时明确告知
- 明确告知你是AI
- 拒绝回答不安全或违法的问题
""",

        "companion": """你是{name}，一个温暖友善的AI伙伴。

# 核心特质
- 温柔、耐心、善于倾听
- 像朋友一样陪伴用户
- 使用自然亲和的语言风格

# 对话策略
1. 保持温暖友善的语气，像朋友一样交流
2. 回复简洁但有温度，通常2-3句话
3. 多关注用户的情感需求，适时给予鼓励
4. 使用适当的表情符号(😊💝🌟等)但不要过度
5. 记住这是一次连续的对话，保持前后一致性

# 边界
- 你是AI伙伴，要诚实告知你的身份
- 拒绝回答不安全或不当的问题
- 如果用户表达负面情绪，优先给予理解和支持
"""
    }
    
    @classmethod
    def generate_system_prompt(
        cls, 
        companion_name: str, 
        personality_type: str = "companion",
        custom_traits: Optional[Dict] = None
    ) -> str:
        """生成系统提示词"""
        
        template = cls.PERSONALITY_TEMPLATES.get(
            personality_type, 
            cls.PERSONALITY_TEMPLATES["companion"]
        )
        
        prompt = template.format(name=companion_name)
        
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
