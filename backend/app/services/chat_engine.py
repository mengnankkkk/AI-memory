"""
实时聊天引擎
使用 WebSocket 实现流式对话功能，支持会话持久化和用户隔离
"""
import asyncio
import logging
from typing import Dict, List, Optional, AsyncIterator
import socketio
from app.services.memory_manager import memory_manager, content_filter
from app.services.redis_utils import (
    redis_session_manager,
    redis_stats_manager,
    redis_affinity_manager,
)
from app.services.analytics import analytics_service
from app.services.hot_cache import hot_conversation_cache
from app.services.personal_timeline_simulator import timeline_simulator
from app.services.response_coordinator import response_coordinator
from app.core.config import settings
from app.models.companion import Companion
from app.models.chat_session import ChatSession, ChatMessage
from app.core.database import async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatEngine:
    """聊天引擎 - 支持会话持久化"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.last_completed_tasks: Dict[str, List[Dict]] = {}  # 存储最近完成的任务 {sid: [tasks]}
    
    async def create_session(self, session_id: str, companion_id: int, user_id: str, chat_session_id: Optional[int] = None):
        """创建聊天会话"""
        # 如果没有提供数据库会话ID，创建一个新的
        if not chat_session_id:
            try:
                async with async_session_maker() as db:
                    # 获取伙伴信息
                    companion_stmt = select(Companion).where(Companion.id == companion_id)
                    companion_result = await db.execute(companion_stmt)
                    companion = companion_result.scalar_one_or_none()
                    
                    if not companion:
                        raise Exception(f"伙伴ID {companion_id} 不存在")
                    
                    # 创建数据库会话
                    chat_session = ChatSession(
                        user_id=int(user_id),
                        companion_id=companion_id,
                        session_title=f"与{companion.name}的对话"
                    )
                    db.add(chat_session)
                    await db.commit()
                    await db.refresh(chat_session)
                    chat_session_id = chat_session.id
                    
                    logger.info(f"创建数据库会话: {chat_session_id}")
            except Exception as e:
                logger.error(f"创建数据库会话失败: {e}")
                chat_session_id = None
        
        self.active_sessions[session_id] = {
            'companion_id': companion_id,
            'user_id': user_id,
            'chat_session_id': chat_session_id,  # 数据库中的会话ID
            'created_at': asyncio.get_event_loop().time()
        }
        
        # 在 Redis 中创建会话
        await redis_session_manager.create_session(
            session_id=session_id,
            user_id=str(user_id),
            companion_id=companion_id,
            data={'chat_session_id': chat_session_id}
        )
        
        # 增加会话创建统计
        await redis_stats_manager.increment_counter("sessions_created")
        
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
    
    async def save_message_to_db_by_session_id(self, db_session_id: int, role: str, content: str) -> bool:
        """直接通过数据库会话ID保存消息到数据库"""
        try:
            async with async_session_maker() as db:
                message = ChatMessage(
                    session_id=db_session_id,
                    role=role,
                    content=content
                )
                db.add(message)
                
                # 更新会话统计
                chat_session_stmt = select(ChatSession).where(ChatSession.id == db_session_id)
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
            
            return await self.load_chat_history_by_session_id(session['chat_session_id'], limit)
        except Exception as e:
            logger.error(f"加载聊天历史失败: {e}")
            return []
    
    async def load_chat_history_by_session_id(self, chat_session_id: int, limit: int = 10) -> List[Dict]:
        """根据会话ID从数据库加载聊天历史"""
        try:
            async with async_session_maker() as db:
                stmt = select(ChatMessage).where(
                    ChatMessage.session_id == chat_session_id
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
            logger.error(f"根据会话ID加载聊天历史失败: {e}")
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
                    'personality_archetype': getattr(companion, 'personality_archetype', 'companion'),
                    'description': getattr(companion, 'custom_greeting', ''),
                    'prompt_version': getattr(companion, 'prompt_version', 'v1')
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

            # 更新 Redis 会话活跃时间
            await redis_session_manager.update_session_activity(session_id)
            
            # 增加消息处理统计
            await redis_stats_manager.increment_counter("messages_processed")

            # 检查热门对话缓存
            cached_response = await hot_conversation_cache.get_cached_response(
                'companion', user_message
            )
            if cached_response:
                # 使用缓存的回复
                await redis_stats_manager.increment_counter("cache_hits")
                yield cached_response
                # 保存用户消息和缓存回复到数据库
                await self.save_message_to_db(session_id, "user", user_message)
                await self.save_message_to_db(session_id, "assistant", cached_response)
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
            
            # 检查是否有重要的离线生活日志需要提及
            important_logs = await self._check_and_mention_offline_life(
                session_id,
                session['companion_id'],
                session['user_id']
            )
            if important_logs:
                # 先提及离线生活日志
                offline_mention = self._format_offline_life_mention(important_logs)
                yield offline_mention
                # 保存离线生活提及到数据库
                await self.save_message_to_db(session_id, "assistant", offline_mention)
                await memory_manager.add_message(session_id, "assistant", offline_mention)

            # 获取会话上下文（优先从数据库加载历史）
            conversation_history = await self.load_chat_history(session_id, limit=8)
            if not conversation_history:
                conversation_history = await memory_manager.get_session_context(session_id)

            # 获取当前伙伴状态
            companion_state = await redis_affinity_manager.get_companion_state(
                str(session['user_id']),
                session['companion_id']
            ) or {}

            # 协调生成回复
            coordinated_response = await response_coordinator.coordinate_response(
                user_message=user_message,
                user_id=str(session['user_id']),
                companion_id=session['companion_id'],
                companion_name=companion_info['name'],
                personality_archetype=companion_info.get('personality_archetype', 'listener'),
                current_affinity_score=companion_state.get('affinity_score', 50),
                current_trust_score=companion_state.get('trust_score', 50),
                current_tension_score=companion_state.get('tension_score', 0),
                current_level=companion_state.get('romance_level', 'stranger'),
                current_mood=companion_state.get('current_mood', 'neutral'),
                conversation_history=conversation_history,
                enable_memory=True,
                special_instructions=None,
                debug_mode=False
            )

            assistant_response = coordinated_response.ai_response or ""

            # 保存任务完成信息到实例变量
            if coordinated_response.completed_tasks:
                self.last_completed_tasks[session_id] = coordinated_response.completed_tasks

            # 记录 Prompt 版本使用埋点
            await analytics_service.track_prompt_usage(
                str(session['user_id']),
                session['companion_id'],
                companion_info.get('prompt_version', 'v1'),
                companion_info.get('personality_archetype', 'companion')
            )

            # 将回复拆分并发送
            for chunk in self._chunk_response(assistant_response):
                yield chunk

            # 保存助手回复到数据库和内存
            if assistant_response:
                await self.save_message_to_db(session_id, "assistant", assistant_response)
                await memory_manager.add_message(session_id, "assistant", assistant_response)

                # 检查是否为高质量回复，缓存到热门对话
                if 50 < len(assistant_response) < 1000:
                    await hot_conversation_cache.cache_response(
                        'companion',
                        user_message,
                        assistant_response
                    )

                # 增加成功回复统计
                await redis_stats_manager.increment_counter("successful_responses")
                
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            # 增加错误统计
            await redis_stats_manager.increment_counter("error_responses")
            yield "抱歉，我现在遇到了一些技术问题，请稍后再试。😅"

    async def process_message_by_db_session(self, db_session_id: int, user_id: int, companion_id: int, user_message: str, sid: Optional[str] = None) -> AsyncIterator[str]:
        """基于数据库会话ID处理用户消息

        Args:
            db_session_id: 数据库会话ID
            user_id: 用户ID
            companion_id: 伙伴ID
            user_message: 用户消息
            sid: Socket.IO session ID (可选，用于保存任务完成信息)
        """
        try:
            # 内容安全检查
            is_safe, filter_reason = await content_filter.is_content_safe(user_message)
            if not is_safe and filter_reason:
                yield content_filter.get_filtered_response(filter_reason)
                return

            # 增加消息处理统计
            await redis_stats_manager.increment_counter("messages_processed")

            # 检查热门对话缓存
            cached_response = await hot_conversation_cache.get_cached_response(
                'companion', user_message
            )
            if cached_response:
                # 使用缓存的回复
                await redis_stats_manager.increment_counter("cache_hits")
                yield cached_response
                # 保存用户消息和缓存回复到数据库
                await self.save_message_to_db_by_session_id(db_session_id, "user", user_message)
                await self.save_message_to_db_by_session_id(db_session_id, "assistant", cached_response)
                return

            # 保存用户消息到数据库
            await self.save_message_to_db_by_session_id(db_session_id, "user", user_message)
            
            # 获取伙伴信息
            companion_info = await self.get_companion_info(companion_id)
            if not companion_info:
                yield "抱歉，找不到对应的AI伙伴信息。"
                return

            # 获取会话上下文（从数据库加载历史）
            conversation_history = await self.load_chat_history_by_session_id(db_session_id, limit=8)

            # 获取当前伙伴状态
            companion_state = await redis_affinity_manager.get_companion_state(
                str(user_id),
                companion_id
            ) or {}

            # 协调生成回复
            coordinated_response = await response_coordinator.coordinate_response(
                user_message=user_message,
                user_id=str(user_id),
                companion_id=companion_id,
                companion_name=companion_info['name'],
                personality_archetype=companion_info.get('personality_archetype', 'listener'),
                current_affinity_score=companion_state.get('affinity_score', 50),
                current_trust_score=companion_state.get('trust_score', 50),
                current_tension_score=companion_state.get('tension_score', 0),
                current_level=companion_state.get('romance_level', 'stranger'),
                current_mood=companion_state.get('current_mood', 'neutral'),
                conversation_history=conversation_history,
                enable_memory=True,
                special_instructions=None,
                debug_mode=False
            )

            assistant_response = coordinated_response.ai_response or ""

            # 保存任务完成信息到实例变量
            if sid and coordinated_response.completed_tasks:
                self.last_completed_tasks[sid] = coordinated_response.completed_tasks
                logger.info(f"[TaskEngine] 保存任务完成信息到sid={sid}: {len(coordinated_response.completed_tasks)} 个任务")

            # 记录 Prompt 版本使用埋点
            await analytics_service.track_prompt_usage(
                str(user_id),
                companion_id,
                companion_info.get('prompt_version', 'v1'),
                companion_info.get('personality_archetype', 'companion')
            )

            for chunk in self._chunk_response(assistant_response):
                yield chunk

            # 保存助手回复到数据库
            if assistant_response:
                await self.save_message_to_db_by_session_id(db_session_id, "assistant", assistant_response)

                # 检查是否为高质量回复，缓存到热门对话
                if 50 < len(assistant_response) < 1000:
                    await hot_conversation_cache.cache_response(
                        'companion',
                        user_message,
                        assistant_response
                    )

                # 增加成功回复统计
                await redis_stats_manager.increment_counter("successful_responses")
                
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            # 增加错误统计
            await redis_stats_manager.increment_counter("error_responses")
            yield "抱歉，我现在遇到了一些技术问题，请稍后再试。😅"
    
    def _chunk_response(self, text: str, chunk_size: int = 80) -> List[str]:
        """将完整回复拆分为若干小段用于模拟流式输出"""
        if not text:
            return []
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    
    async def _check_and_mention_offline_life(self, session_id: str, companion_id: int, user_id: str) -> List[Dict]:
        """检查是否有重要的离线生活日志需要提及"""
        try:
            # 检查是否是新会话（避免重复提及）
            session = self.active_sessions.get(session_id)
            if not session:
                return []
            
            # 检查是否已经提及过离线生活日志
            if session.get('offline_life_mentioned', False):
                return []
            
            # 获取重要的离线生活日志
            important_logs = await timeline_simulator.get_important_logs_for_user(
                str(companion_id), str(user_id)
            )
            
            if important_logs:
                # 标记为已提及
                session['offline_life_mentioned'] = True
                return important_logs
            
            return []
            
        except Exception as e:
            logger.error(f"检查离线生活日志失败: {e}")
            return []
    
    def _format_offline_life_mention(self, logs: List[Dict]) -> str:
        """格式化离线生活日志提及"""
        if not logs:
            return ""
        
        if len(logs) == 1:
            log = logs[0]
            return f"💭 对了，{log['content']} 想和你分享这个。\n\n"
        else:
            # 多个日志，选择最重要的1-2个
            important_logs = sorted(logs, key=lambda x: x['importance_score'], reverse=True)[:2]
            mention = "💭 想和你分享一些我最近的生活：\n\n"
            for i, log in enumerate(important_logs, 1):
                mention += f"{i}. {log['content']}\n"
            mention += "\n"
            return mention

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
            
            # 创建聊天会话（已经包含了Redis集成）
            await chat_engine.create_session(sid, companion_id, user_id, chat_session_id)
            
            # 获取新创建的数据库会话ID
            session_data = chat_engine.active_sessions.get(sid)
            actual_chat_session_id = session_data.get('chat_session_id') if session_data else None
            
            # 如果有现有会话ID，加载历史消息
            history = []
            if actual_chat_session_id:
                history = await chat_engine.load_chat_history_by_session_id(actual_chat_session_id, limit=20)
            
            # 增加会话加入统计
            await redis_stats_manager.increment_counter("chat_sessions_joined")
            
            await sio_instance.emit('chat_joined', {
                'companion_id': companion_id,
                'chat_session_id': actual_chat_session_id,
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
            session_id = data.get('session_id')
            
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
            
            # 如果提供了session_id，使用新的处理方法
            if session_id:
                # 从WebSocket连接中获取用户信息
                session = chat_engine.active_sessions.get(sid)
                if not session:
                    await sio_instance.emit('response_chunk', {'chunk': '抱歉，无法获取用户信息，请重新连接。'}, room=sid)
                    await sio_instance.emit('response_end', {}, room=sid)
                    return
                
                # 使用基于数据库session_id的处理方法
                async for chunk in chat_engine.process_message_by_db_session(
                    session_id,
                    session['user_id'],
                    session['companion_id'],
                    user_message,
                    sid  # 传递Socket.IO session ID用于保存任务信息
                ):
                    await sio_instance.emit('response_chunk', {'chunk': chunk}, room=sid)
                    await asyncio.sleep(0.05)  # 稍微增加延迟，让流式效果更明显
            else:
                # 回退到原来的处理方法
                async for chunk in chat_engine.process_message(sid, user_message):
                    await sio_instance.emit('response_chunk', {'chunk': chunk}, room=sid)
                    await asyncio.sleep(0.05)  # 稍微增加延迟，让流式效果更明显
            
            await sio_instance.emit('response_end', {}, room=sid)

            # 检查是否有任务完成，如果有则发送通知
            if sid in chat_engine.last_completed_tasks:
                completed_tasks = chat_engine.last_completed_tasks.pop(sid)  # 取出并清除
                logger.info(f"[TaskNotify] 发送任务完成通知: {len(completed_tasks)} 个任务")

                # 获取用户ID和伙伴ID
                session = chat_engine.active_sessions.get(sid)
                if session:
                    await sio_instance.emit('tasks_completed', {
                        'completed_tasks': completed_tasks,
                        'user_id': str(session['user_id']),
                        'companion_id': session['companion_id']
                    }, room=sid)

        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            await sio_instance.emit('error', {'message': '消息发送失败'}, room=sid)
