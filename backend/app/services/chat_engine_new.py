"""
实时聊天引擎
使用 WebSocket 实现流式对话功能，支持会话持久化和用户隔离
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, AsyncIterator
import socketio
from app.services.streaming_llm import streaming_llm_service
from app.services.memory_manager import memory_manager, SystemPromptGenerator, content_filter
from app.core.config import settings
from app.models.companion import Companion
from app.models.chat_session import ChatSession, ChatMessage
from app.core.database import get_async_session, async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatEngine:
    """聊天引擎 - 支持会话持久化"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
    
    async def create_session(self, session_id: str, companion_id: int, user_id: str, chat_session_id: Optional[int] = None):
        """创建聊天会话"""
        self.active_sessions[session_id] = {
            'companion_id': companion_id,
            'user_id': user_id,
            'chat_session_id': chat_session_id,  # 数据库中的会话ID
            'created_at': asyncio.get_event_loop().time()
        }
        
        logger.info(f"创建聊天会话: {session_id}, 伙伴ID: {companion_id}, 数据库会话ID: {chat_session_id}")
    
    async def save_message_to_db(self, session_id: str, role: str, content: str) -> bool:
        """保存消息到数据库"""
        try:
            session = self.active_sessions.get(session_id)
            if not session or not session.get('chat_session_id'):
                return False
            
            async with async_session_maker() as db:
                message = ChatMessage(
                    session_id=session['chat_session_id'],
                    role=role,
                    content=content
                )
                db.add(message)
                
                # 更新会话统计
                chat_session_stmt = select(ChatSession).where(ChatSession.id == session['chat_session_id'])
                result = await db.execute(chat_session_stmt)
                chat_session = result.scalar_one_or_none()
                
                if chat_session:
                    chat_session.total_messages += 1
                
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"保存消息到数据库失败: {e}")
            return False
    
    async def load_chat_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """从数据库加载聊天历史"""
        try:
            session = self.active_sessions.get(session_id)
            if not session or not session.get('chat_session_id'):
                return []
            
            async with async_session_maker() as db:
                stmt = select(ChatMessage).where(
                    ChatMessage.session_id == session['chat_session_id']
                ).order_by(ChatMessage.timestamp.desc()).limit(limit)
                
                result = await db.execute(stmt)
                messages = result.scalars().all()
                
                # 转换为字典格式并按时间正序排列
                history = []
                for msg in reversed(messages):
                    history.append({
                        'role': msg.role,
                        'content': msg.content,
                        'timestamp': msg.timestamp.isoformat()
                    })
                
                return history
        except Exception as e:
            logger.error(f"加载聊天历史失败: {e}")
            return []
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """获取聊天会话"""
        return self.active_sessions.get(session_id)
    
    async def remove_session(self, session_id: str):
        """移除聊天会话"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            await memory_manager.clear_session(session_id)
            logger.info(f"移除聊天会话: {session_id}")
    
    async def get_companion_info(self, companion_id: int) -> Optional[Dict]:
        """获取伙伴信息"""
        try:
            async with async_session_maker() as db:
                result = await db.execute(
                    select(Companion).where(Companion.id == companion_id)
                )
                companion = result.scalar_one_or_none()
                
                if not companion:
                    return None
                
                return {
                    'id': companion.id,
                    'name': companion.name,
                    'personality': getattr(companion, 'personality_archetype', 'companion'),
                    'description': getattr(companion, 'custom_greeting', '')
                }
        except Exception as e:
            logger.error(f"获取伙伴信息失败: {e}")
            return None
    
    async def process_message(self, session_id: str, user_message: str) -> AsyncIterator[str]:
        """处理用户消息并流式返回回复"""
        session = await self.get_session(session_id)
        if not session:
            yield "抱歉，会话已过期，请刷新页面重试。"
            return
        
        try:
            # 内容安全检查
            is_safe, filter_reason = await content_filter.is_content_safe(user_message)
            if not is_safe and filter_reason:
                yield content_filter.get_filtered_response(filter_reason)
                return
            
            # 保存用户消息到数据库
            await self.save_message_to_db(session_id, "user", user_message)
            
            # 添加用户消息到内存会话
            await memory_manager.add_message(session_id, "user", user_message)
            
            # 获取伙伴信息
            companion_info = await self.get_companion_info(session['companion_id'])
            if not companion_info:
                yield "抱歉，找不到对应的AI伙伴信息。"
                return
            
            # 生成系统提示词
            system_prompt = SystemPromptGenerator.generate_system_prompt(
                companion_name=companion_info['name'],
                personality_type=companion_info.get('personality', 'companion')
            )
            
            # 获取会话上下文（优先从数据库加载历史）
            db_history = await self.load_chat_history(session_id, limit=8)
            if db_history:
                # 使用数据库历史
                context_messages = db_history
            else:
                # 回退到内存会话
                context_messages = await memory_manager.get_session_context(session_id)
            
            # 调用 LLM 进行流式回复
            assistant_response = ""
            async for chunk in self.stream_llm_response(system_prompt, context_messages):
                assistant_response += chunk
                yield chunk
            
            # 保存助手回复到数据库和内存
            if assistant_response:
                await self.save_message_to_db(session_id, "assistant", assistant_response)
                await memory_manager.add_message(session_id, "assistant", assistant_response)
                
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            yield "抱歉，我现在遇到了一些技术问题，请稍后再试。😅"
    
    async def stream_llm_response(self, system_prompt: str, messages: List[Dict]) -> AsyncIterator[str]:
        """流式调用 LLM"""
        try:
            # 构建 LLM 消息格式，包含系统提示词
            llm_messages = [{"role": "system", "content": system_prompt}]
            
            for msg in messages:
                if msg['role'] in ['user', 'assistant']:
                    llm_messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
            
            # 使用流式 LLM 服务
            assistant_response = ""
            async for chunk_type, content in streaming_llm_service.stream_chat_completion(llm_messages):
                if chunk_type == "content":
                    # 内容过滤
                    is_safe, filter_reason = await content_filter.is_content_safe(content)
                    if not is_safe and filter_reason:
                        logger.warning(f"Content filtered in streaming response: {filter_reason}")
                        filtered_content = content_filter.get_filtered_response(filter_reason)
                    else:
                        filtered_content = content
                    
                    assistant_response += filtered_content
                    yield filtered_content
                    
                elif chunk_type == "done":
                    # 流式传输完成
                    break
                    
        except Exception as e:
            logger.error(f"LLM 流式调用失败: {e}")
            yield "抱歉，我现在有点累了，请稍后再和我聊天吧。😴"

# 全局聊天引擎实例
chat_engine = ChatEngine()

def get_chat_engine():
    """获取聊天引擎实例"""
    return chat_engine

def register_socketio_events(sio_instance):
    """注册Socket.IO事件处理器到外部sio实例"""
    
    @sio_instance.event
    async def connect(sid, environ):
        """客户端连接"""
        logger.info(f"客户端连接: {sid}")
        await sio_instance.emit('connected', {'message': '连接成功！'}, room=sid)

    @sio_instance.event  
    async def disconnect(sid):
        """客户端断开连接"""
        logger.info(f"客户端断开连接: {sid}")
        # 清理会话
        await chat_engine.remove_session(sid)

    @sio_instance.event
    async def join_chat(sid, data):
        """加入聊天"""
        try:
            companion_id = data.get('companion_id')
            user_id = data.get('user_id', 'anonymous')
            chat_session_id = data.get('chat_session_id')  # 可选的数据库会话ID
            
            if not companion_id:
                await sio_instance.emit('error', {'message': '缺少伙伴ID'}, room=sid)
                return
            
            # 创建聊天会话
            await chat_engine.create_session(sid, companion_id, user_id, chat_session_id)
            
            # 如果有现有会话ID，加载历史消息
            history = []
            if chat_session_id:
                history = await chat_engine.load_chat_history(sid, limit=20)
            
            await sio_instance.emit('chat_joined', {
                'companion_id': companion_id,
                'chat_session_id': chat_session_id,
                'message': '已加入聊天，可以开始对话了！',
                'history': history
            }, room=sid)
            
        except Exception as e:
            logger.error(f"加入聊天失败: {e}")
            await sio_instance.emit('error', {'message': '加入聊天失败'}, room=sid)

    @sio_instance.event
    async def send_message(sid, data):
        """发送消息 - 流式输出"""
        try:
            user_message = data.get('message', '').strip()
            
            if not user_message:
                await sio_instance.emit('error', {'message': '消息不能为空'}, room=sid)
                return
            
            # 先确认收到消息
            await sio_instance.emit('message_received', {
                'message': user_message,
                'timestamp': asyncio.get_event_loop().time()
            }, room=sid)
            
            # 开始流式回复
            await sio_instance.emit('response_start', {}, room=sid)
            
            # 使用聊天引擎进行流式处理
            async for chunk in chat_engine.process_message(sid, user_message):
                await sio_instance.emit('response_chunk', {'chunk': chunk}, room=sid)
                await asyncio.sleep(0.05)  # 稍微增加延迟，让流式效果更明显
            
            await sio_instance.emit('response_end', {}, room=sid)
                
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            await sio_instance.emit('error', {'message': '消息发送失败'}, room=sid)
