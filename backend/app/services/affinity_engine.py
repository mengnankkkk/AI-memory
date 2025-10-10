"""
AI情感计算引擎 (Affinity Engine)
使用两阶段LLM调用架构，实现真正的AI级别情感理解
"""
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.services.llm.factory import llm_service
from app.config.affinity_levels import (
    get_level_by_score,
    get_level_config,
    LEVEL_ORDER,
    normalize_level_key
)
from app.config.response_rules import get_response_rule
from app.services.affinity_protector import AffinityProtector
from app.services.redis_utils import redis_affinity_manager, redis_stats_manager
from app.core.prompts import get_system_prompt
from app.core.database import async_session_maker
from app.models.relationship import (
    CompanionRelationshipState,
    RelationshipHistory,
    EmotionLog
)

logger = logging.getLogger("affinity_engine")


@dataclass
class EmotionAnalysis:
    """LLM情感分析结果"""
    primary_emotion: str  # 主要情感: positive/negative/neutral/romantic
    emotion_intensity: float  # 情感强度 0-1
    detected_emotions: List[str]  # 具体情感: joy, gratitude, love, anger, sadness等
    user_intent: str  # 用户意图: greeting, sharing, question, compliment, complaint等
    is_appropriate: bool  # 是否适合当前关系等级
    violation_reason: str  # 违规原因（如果有）
    suggested_affinity_change: int  # LLM建议的好感度变化
    suggested_trust_change: int  # LLM建议的信任度变化
    suggested_tension_change: int  # LLM建议的紧张度变化
    key_points: List[str]  # 消息关键点
    is_memorable: bool  # 是否值得记忆


@dataclass
class ProcessResult:
    """完整的处理结果"""
    # 情感分析
    emotion_analysis: EmotionAnalysis

    # 状态变化（已应用保护机制）
    affinity_change: int
    trust_change: int
    tension_change: int

    # 新状态
    new_affinity_score: int
    new_trust_score: int
    new_tension_score: int
    new_level: str
    new_level_name: str

    # 等级变化
    level_changed: bool
    level_up: bool
    level_down: bool
    level_change_message: str

    # 回复指导
    response_guidance: Dict

    # 增强的系统Prompt
    enhanced_system_prompt: str

    # 保护机制信息
    protection_warnings: List[str]
    protection_reason: str

    # 趋势分析
    trend: str
    recovery_suggestion: str


class AffinityEngine:
    """
    AI情感计算引擎

    核心职责:
    1. 使用LLM分析用户消息的情感和意图（第一阶段LLM调用）
    2. 计算所有状态变化（affinity, trust, tension）
    3. 应用保护机制
    4. 生成增强的系统Prompt
    5. 返回完整的ProcessResult
    """

    def __init__(self):
        self.protector = AffinityProtector()

    async def process_user_message(
        self,
        user_message: str,
        current_affinity_score: int,
        current_trust_score: int,
        current_tension_score: int,
        current_level: str,
        current_mood: str,
        companion_name: str,
        user_id: str,
        companion_id: int,
        recent_memories: Optional[List[str]] = None,
        user_facts: Optional[Dict] = None
    ) -> ProcessResult:
        """
        处理用户消息的完整流程

        这是引擎的核心方法，执行所有逻辑并返回完整结果
        """
        normalized_level = normalize_level_key(current_level)
        if normalized_level != current_level:
            logger.warning(
                f"[AffinityEngine] 非标准等级标识 '{current_level}'，已归一化为 '{normalized_level}'"
            )
        current_level = normalized_level

        logger.info(f"[AffinityEngine] 开始处理消息 - 用户:{user_id}, 当前等级:{current_level}, 分数:{current_affinity_score}")

        # 第一阶段：使用LLM进行情感分析和评估
        emotion_analysis = await self._analyze_with_llm(
            user_message=user_message,
            current_level=current_level,
            current_affinity_score=current_affinity_score,
            current_mood=current_mood,
            companion_name=companion_name
        )

        logger.info(
            f"[AffinityEngine] LLM分析结果 - 情感:{emotion_analysis.primary_emotion}, "
            f"强度:{emotion_analysis.emotion_intensity:.2f}, "
            f"建议变化:{emotion_analysis.suggested_affinity_change:+d}"
        )

        # 应用保护机制
        protection_result = self.protector.protect_and_adjust(
            current_affinity_score,
            emotion_analysis.suggested_affinity_change,
            reason=f"{emotion_analysis.primary_emotion}_{emotion_analysis.user_intent}"
        )

        # 计算新状态
        new_affinity_score = current_affinity_score + protection_result.adjusted_change
        new_trust_score = min(100, max(0, current_trust_score + emotion_analysis.suggested_trust_change))
        new_tension_score = min(100, max(0, current_tension_score + emotion_analysis.suggested_tension_change))

        # 获取新等级
        new_level = get_level_by_score(new_affinity_score)
        new_level_config = get_level_config(new_level)

        # 检测等级变化
        level_changed = current_level != new_level
        level_up = False
        level_down = False
        level_change_message = ""

        if level_changed:
            current_index = LEVEL_ORDER.index(current_level)
            new_index = LEVEL_ORDER.index(new_level)
            level_up = new_index > current_index
            level_down = new_index < current_index

            if level_up:
                level_change_message = self._get_level_up_message(new_level)
            else:
                level_change_message = self._get_level_down_message()

        # 生成回复指导
        response_guidance = self._generate_response_guidance(
            new_level,
            new_level_config,
            current_mood,
            emotion_analysis,
            level_changed,
            level_up
        )

        # 生成增强的系统Prompt（集成记忆）
        enhanced_system_prompt = self._build_enhanced_system_prompt(
            companion_name=companion_name,
            current_level=new_level,
            current_mood=current_mood,
            affinity_score=new_affinity_score,
            trust_score=new_trust_score,
            tension_score=new_tension_score,
            recent_memories=recent_memories,
            user_facts=user_facts,
            emotion_analysis=emotion_analysis
        )

        # 获取趋势
        trend = self.protector.get_recent_trend()
        recovery_suggestion = self.protector.suggest_recovery_action(new_affinity_score)

        logger.info(
            f"[AffinityEngine] 处理完成 - 新分数:{new_affinity_score}, "
            f"新等级:{new_level_config.name}, 等级变化:{level_changed}"
        )

        # 🔥 自动更新数据库 - 核心集成功能
        try:
            await self._update_database_automatically(
                user_id=user_id,
                companion_id=companion_id,
                emotion_analysis=emotion_analysis,
                affinity_change=protection_result.adjusted_change,
                trust_change=emotion_analysis.suggested_trust_change,
                tension_change=emotion_analysis.suggested_tension_change,
                new_affinity_score=new_affinity_score,
                new_trust_score=new_trust_score,
                new_tension_score=new_tension_score,
                new_level=new_level,
                level_changed=level_changed,
                user_message=user_message,
                previous_affinity_score=current_affinity_score,
                previous_trust_score=current_trust_score,
                previous_tension_score=current_tension_score,
                previous_level=current_level
            )
            logger.info(f"[AffinityEngine] 数据库自动更新完成")
        except Exception as e:
            logger.warning(f"[AffinityEngine] 数据库自动更新失败，但不影响主流程: {e}")

        return ProcessResult(
            emotion_analysis=emotion_analysis,
            affinity_change=protection_result.adjusted_change,
            trust_change=emotion_analysis.suggested_trust_change,
            tension_change=emotion_analysis.suggested_tension_change,
            new_affinity_score=new_affinity_score,
            new_trust_score=new_trust_score,
            new_tension_score=new_tension_score,
            new_level=new_level,
            new_level_name=new_level_config.name,
            level_changed=level_changed,
            level_up=level_up,
            level_down=level_down,
            level_change_message=level_change_message,
            response_guidance=response_guidance,
            enhanced_system_prompt=enhanced_system_prompt,
            protection_warnings=protection_result.warnings,
            protection_reason=protection_result.protection_reason,
            trend=trend,
            recovery_suggestion=recovery_suggestion
        )

    async def _analyze_with_llm(
        self,
        user_message: str,
        current_level: str,
        current_affinity_score: int,
        current_mood: str,
        companion_name: str
    ) -> EmotionAnalysis:
        """
        第一阶段LLM调用：情感分析和评估

        这是引擎的核心创新点：使用LLM的理解能力而非关键词匹配
        """
        level_config = get_level_config(current_level)

        # 构建分析专用的Prompt
        analysis_prompt = f"""你是一个专业的情感分析AI。请分析用户发送给AI伙伴"{companion_name}"的以下消息。

【当前关系状态】
- 关系等级: {level_config.name} ({level_config.description})
- 好感度分数: {current_affinity_score}/1000
- 亲密度: {level_config.intimacy_level}/10
- 当前心情: {current_mood}

【用户消息】
"{user_message}"

【分析任务】
请从以下维度分析这条消息，并以JSON格式返回结果：

1. **primary_emotion**: 主要情感类型 (positive/negative/neutral/romantic)
2. **emotion_intensity**: 情感强度 (0-1的浮点数)
3. **detected_emotions**: 具体检测到的情感，从以下选择：
   - 积极: joy(喜悦), gratitude(感谢), excitement(兴奋), affection(关爱), pride(自豪)
   - 消极: anger(愤怒), sadness(悲伤), frustration(沮丧), disappointment(失望), fear(恐惧)
   - 浪漫: love(爱意), longing(思念), shyness(害羞), flirtation(调情)
4. **user_intent**: 用户意图 (greeting/sharing/question/compliment/complaint/request/confession)
5. **is_appropriate**: 考虑当前关系等级，这条消息的亲密程度是否合适？(true/false)
   - 例如：在"陌生"阶段说"宝贝我爱你"就是不合适的
6. **violation_reason**: 如果不合适，简述原因
7. **suggested_affinity_change**: 建议的好感度变化 (-50到+50之间)
   - 考虑因素：情感积极性、消息长度、真诚度、合适性
8. **suggested_trust_change**: 建议的信任度变化 (-10到+10)
9. **suggested_tension_change**: 建议的紧张度变化 (-10到+10)
10. **key_points**: 消息的关键点（1-3个短语）
11. **is_memorable**: 这条消息是否值得长期记忆？(true/false)

【输出格式】
请严格按照以下JSON格式输出，不要包含任何其他文字：
```json
{{
    "primary_emotion": "positive",
    "emotion_intensity": 0.8,
    "detected_emotions": ["joy", "gratitude"],
    "user_intent": "sharing",
    "is_appropriate": true,
    "violation_reason": "",
    "suggested_affinity_change": 8,
    "suggested_trust_change": 2,
    "suggested_tension_change": 0,
    "key_points": ["分享喜悦", "表达感谢"],
    "is_memorable": true
}}
```

现在开始分析："""

        try:
            # 调用LLM进行分析
            messages = [{"role": "user", "content": analysis_prompt}]
            llm_response = await llm_service.chat_completion(messages)

            # 提取JSON
            json_str = self._extract_json(llm_response)
            analysis_data = json.loads(json_str)

            # 构建EmotionAnalysis对象
            return EmotionAnalysis(
                primary_emotion=analysis_data.get("primary_emotion", "neutral"),
                emotion_intensity=float(analysis_data.get("emotion_intensity", 0.5)),
                detected_emotions=analysis_data.get("detected_emotions", []),
                user_intent=analysis_data.get("user_intent", "unknown"),
                is_appropriate=analysis_data.get("is_appropriate", True),
                violation_reason=analysis_data.get("violation_reason", ""),
                suggested_affinity_change=int(analysis_data.get("suggested_affinity_change", 0)),
                suggested_trust_change=int(analysis_data.get("suggested_trust_change", 0)),
                suggested_tension_change=int(analysis_data.get("suggested_tension_change", 0)),
                key_points=analysis_data.get("key_points", []),
                is_memorable=analysis_data.get("is_memorable", False)
            )

        except Exception as e:
            logger.error(f"[AffinityEngine] LLM分析失败: {e}，使用降级方案")
            # 降级方案：返回中性分析
            return EmotionAnalysis(
                primary_emotion="neutral",
                emotion_intensity=0.3,
                detected_emotions=[],
                user_intent="unknown",
                is_appropriate=True,
                violation_reason="",
                suggested_affinity_change=1,
                suggested_trust_change=0,
                suggested_tension_change=0,
                key_points=[],
                is_memorable=False
            )

    def _build_analysis_prompt(
        self, 
        user_message: str, 
        current_level: str, 
        current_affinity_score: int, 
        current_mood: str, 
        companion_name: str
    ) -> str:
        """构建LLM情感分析提示词"""
        return f"""你是一个专业的情感分析AI，专门分析用户与AI伙伴之间的对话情感。

当前状态：
- 伙伴名称：{companion_name}
- 关系等级：{current_level}
- 好感度分数：{current_affinity_score}/1000
- 当前心情：{current_mood}

请分析用户消息的情感和意图，并以JSON格式返回结果：

{{
    "primary_emotion": "positive/negative/neutral/romantic",
    "emotion_intensity": 0.7,
    "detected_emotions": ["joy", "gratitude"],
    "user_intent": "greeting/sharing/question/compliment/complaint",
    "is_appropriate": true,
    "violation_reason": "",
    "suggested_affinity_change": 5,
    "suggested_trust_change": 2,
    "suggested_tension_change": 0,
    "key_points": ["用户表达了感谢"],
    "is_memorable": true
}}

分析原则：
1. 好感度变化范围：-20到+20
2. 信任度/紧张度变化范围：-10到+10
3. 根据当前关系等级判断内容是否合适
4. 重要或有意义的对话标记为memorable"""

    def _parse_llm_analysis(self, raw_analysis: str) -> Dict:
        """解析LLM返回的分析结果"""
        try:
            # 尝试提取JSON
            import re
            json_match = re.search(r'\{.*\}', raw_analysis, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # 如果没有找到JSON，使用默认值
                return self._get_default_analysis()
        except json.JSONDecodeError:
            logger.warning(f"[AffinityEngine] 无法解析LLM分析结果，使用默认值")
            return self._get_default_analysis()

    def _get_default_analysis(self) -> Dict:
        """获取默认的分析结果"""
        return {
            "primary_emotion": "neutral",
            "emotion_intensity": 0.5,
            "detected_emotions": ["neutral"],
            "user_intent": "chat",
            "is_appropriate": True,
            "violation_reason": "",
            "suggested_affinity_change": 0,
            "suggested_trust_change": 0,
            "suggested_tension_change": 0,
            "key_points": [],
            "is_memorable": False
        }

    async def _update_database_automatically(
        self,
        user_id: str,
        companion_id: int,
        emotion_analysis: EmotionAnalysis,
        affinity_change: int,
        trust_change: int,
        tension_change: int,
        new_affinity_score: int,
        new_trust_score: int,
        new_tension_score: int,
        new_level: str,
        level_changed: bool,
        user_message: str,
        previous_affinity_score: int,
        previous_trust_score: int,
        previous_tension_score: int,
        previous_level: str
    ):
        """
        🔥 自动更新数据库 - 核心集成功能
        
        这个方法实现了用户每一句话的自动化处理：
        1. 更新Redis缓存
        2. 更新关系状态到数据库
        3. 记录情感日志
        4. 记录关系变化历史
        5. 更新统计数据
        """
        try:
            # 1. 更新Redis缓存
            await redis_affinity_manager.update_affinity(
                user_id,
                companion_id,
                affinity_change,
                trust_change,
                tension_change,
                "chat"
            )
            
            # 2. 如果值得记忆，添加到记忆中
            if emotion_analysis.is_memorable:
                await redis_affinity_manager.add_memory(
                    user_id,
                    companion_id,
                    user_message,
                    "conversation"
                )
            
            # 3. 更新统计数据
            await redis_stats_manager.increment_counter("interactions_analyzed")
            await redis_stats_manager.increment_counter(f"sentiment_{emotion_analysis.primary_emotion}")
            
            # 4. 更新数据库（如果可用）
            try:
                updated_state = await redis_affinity_manager.get_companion_state(user_id, companion_id)

                # 这里我们使用依赖注入的方式获取数据库会话
                # 注意：这是一个简化的实现，实际项目中可能需要更复杂的数据库管理
                await self._update_relationship_state_db(
                    user_id, companion_id, new_affinity_score, 
                    new_trust_score, new_tension_score, new_level,
                    affinity_change=affinity_change,
                    trust_change=trust_change,
                    tension_change=tension_change,
                    emotion_analysis=emotion_analysis,
                    state_snapshot=updated_state
                )
                
                # 5. 记录情感日志
                await self._log_emotion_to_db(
                    user_id, companion_id, emotion_analysis, 
                    affinity_change, trust_change, tension_change, user_message
                )
                
                # 6. 记录关系变化历史
                if level_changed:
                    await self._log_relationship_change_db(
                        user_id=user_id,
                        companion_id=companion_id,
                        change_type="level_change",
                        old_value=previous_level,
                        new_value=new_level,
                        delta=None,
                        reason=f"好感度达到{new_affinity_score}",
                        context={
                            "previous_affinity": previous_affinity_score,
                            "previous_trust": previous_trust_score,
                            "previous_tension": previous_tension_score,
                            "new_affinity": new_affinity_score,
                            "new_trust": new_trust_score,
                            "new_tension": new_tension_score,
                            "tension_change": tension_change,
                            "trust_change": trust_change
                        }
                    )
                
                if abs(affinity_change) >= 5:  # 只记录重要的好感度变化
                    await self._log_relationship_change_db(
                        user_id=user_id,
                        companion_id=companion_id,
                        change_type="affinity_change",
                        old_value=str(previous_affinity_score),
                        new_value=str(new_affinity_score),
                        delta=affinity_change,
                        reason=f"情感分析：{emotion_analysis.primary_emotion}",
                        context={
                            "user_intent": emotion_analysis.user_intent,
                            "is_appropriate": emotion_analysis.is_appropriate,
                            "detected_emotions": emotion_analysis.detected_emotions
                        }
                    )
                    
            except Exception as db_error:
                logger.warning(f"[AffinityEngine] 数据库更新失败，但Redis已更新: {db_error}")
                # 数据库失败不影响核心功能，Redis作为主要存储
            
            logger.info(
                f"[AffinityEngine] 自动化更新完成 - 用户:{user_id}, "
                f"好感度变化:{affinity_change:+d}, 新分数:{new_affinity_score}"
            )
            
        except Exception as e:
            logger.error(f"[AffinityEngine] 自动化更新失败: {e}")
            # 即使更新失败，也不应该影响主流程
            raise

    async def _update_relationship_state_db(
        self,
        user_id: str,
        companion_id: int,
        affinity_score: int,
        trust_score: int,
        tension_score: int,
        romance_level: str,
        *,
        affinity_change: int,
        trust_change: int,
        tension_change: int,
        emotion_analysis: EmotionAnalysis,
        state_snapshot: Optional[Dict] = None
    ):
        """更新关系状态到数据库"""
        user_id_str = str(user_id)
        companion_id_str = str(companion_id)
        now = datetime.now(timezone.utc)

        try:
            async with async_session_maker() as session:
                try:
                    stmt = select(CompanionRelationshipState).where(
                        CompanionRelationshipState.user_id == user_id_str,
                        CompanionRelationshipState.companion_id == companion_id_str
                    )
                    result = await session.execute(stmt)
                    relationship_state = result.scalar_one_or_none()

                    if relationship_state:
                        relationship_state.affinity_score = affinity_score
                        relationship_state.trust_score = trust_score
                        relationship_state.tension_score = tension_score
                        relationship_state.romance_stage = romance_level
                        if state_snapshot and isinstance(state_snapshot, dict):
                            relationship_state.current_mood = state_snapshot.get("current_mood", relationship_state.current_mood)
                            relationship_state.total_interactions = state_snapshot.get("total_interactions", relationship_state.total_interactions)
                        else:
                            relationship_state.total_interactions = (relationship_state.total_interactions or 0) + 1
                        if affinity_change > 0:
                            relationship_state.positive_interactions = (relationship_state.positive_interactions or 0) + 1
                        elif affinity_change < 0:
                            relationship_state.negative_interactions = (relationship_state.negative_interactions or 0) + 1
                        relationship_state.last_interaction_at = now

                        flags = relationship_state.special_flags or {}
                        flags.update({
                            "last_primary_emotion": emotion_analysis.primary_emotion,
                            "last_user_intent": emotion_analysis.user_intent,
                            "last_affinity_change": affinity_change,
                            "last_trust_change": trust_change,
                            "last_tension_change": tension_change,
                            "last_update_at": now.isoformat()
                        })
                        relationship_state.special_flags = flags
                    else:
                        total_interactions = 1
                        if state_snapshot and isinstance(state_snapshot, dict):
                            total_interactions = state_snapshot.get("total_interactions", total_interactions)

                        relationship_state = CompanionRelationshipState(
                            user_id=user_id_str,
                            companion_id=companion_id_str,
                            affinity_score=affinity_score,
                            trust_score=trust_score,
                            tension_score=tension_score,
                            romance_stage=romance_level,
                            current_mood=(state_snapshot or {}).get("current_mood", "neutral"),
                            total_interactions=total_interactions,
                            positive_interactions=1 if affinity_change > 0 else 0,
                            negative_interactions=1 if affinity_change < 0 else 0,
                            special_flags={
                                "last_primary_emotion": emotion_analysis.primary_emotion,
                                "last_user_intent": emotion_analysis.user_intent,
                                "last_affinity_change": affinity_change,
                                "last_trust_change": trust_change,
                                "last_tension_change": tension_change,
                                "last_update_at": now.isoformat()
                            },
                            last_interaction_at=now
                        )
                        session.add(relationship_state)

                    await session.commit()
                except SQLAlchemyError:
                    await session.rollback()
                    raise
        except SQLAlchemyError as db_error:
            logger.warning(f"[AffinityEngine] 更新关系状态失败: {db_error}")


    async def _log_emotion_to_db(
        self, user_id: str, companion_id: int, 
        emotion_analysis: EmotionAnalysis, 
        affinity_change: int, trust_change: int, 
        tension_change: int, user_message: str
    ):
        """记录情感日志到数据库"""
        try:
            async with async_session_maker() as session:
                try:
                    log_entry = EmotionLog(
                        user_id=str(user_id),
                        companion_id=str(companion_id),
                        primary_emotion=emotion_analysis.primary_emotion,
                        emotion_intensity=int(emotion_analysis.emotion_intensity * 100),
                        detected_emotions=emotion_analysis.detected_emotions,
                        user_intent=emotion_analysis.user_intent,
                        affinity_change=affinity_change,
                        trust_change=trust_change,
                        tension_change=tension_change,
                        is_memorable=emotion_analysis.is_memorable,
                        is_appropriate=emotion_analysis.is_appropriate,
                        user_message_summary=user_message[:500]
                    )

                    session.add(log_entry)
                    await session.commit()
                except SQLAlchemyError:
                    await session.rollback()
                    raise
        except SQLAlchemyError as db_error:
            logger.warning(f"[AffinityEngine] 写入情感日志失败: {db_error}")

    async def _log_relationship_change_db(
        self,
        *,
        user_id: str,
        companion_id: int,
        change_type: str,
        old_value: Optional[str],
        new_value: Optional[str],
        delta: Optional[int],
        reason: str,
        context: Optional[Dict] = None
    ):
        """记录关系变化历史到数据库"""
        try:
            async with async_session_maker() as session:
                try:
                    history_entry = RelationshipHistory(
                        user_id=str(user_id),
                        companion_id=str(companion_id),
                        change_type=change_type,
                        old_value=old_value,
                        new_value=new_value,
                        delta=delta,
                        trigger_reason=reason,
                        trigger_context=context or {}
                    )

                    session.add(history_entry)
                    await session.commit()
                except SQLAlchemyError:
                    await session.rollback()
                    raise
        except SQLAlchemyError as db_error:
            logger.warning(f"[AffinityEngine] 写入关系历史失败: {db_error}")

    def _extract_json(self, text: str) -> str:
        """从LLM回复中提取JSON"""
        # 尝试提取 ```json ... ``` 块
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        else:
            # 尝试查找第一个 { 到最后一个 }
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                return text[start:end]
        return text

    def _build_enhanced_system_prompt(
        self,
        companion_name: str,
        current_level: str,
        current_mood: str,
        affinity_score: int,
        trust_score: int,
        tension_score: int,
        recent_memories: Optional[List[str]],
        user_facts: Optional[Dict],
        emotion_analysis: EmotionAnalysis
    ) -> str:
        """
        构建增强的系统Prompt

        关键创新：融合三层记忆系统
        """
        level_config = get_level_config(current_level)
        response_rule = get_response_rule(current_level)

        # 基础部分
        prompt_parts = [
            f"# 你的身份",
            f"你是{companion_name}。",
            "",
            f"# 当前关系状态",
            f"- 关系等级: {level_config.name} ({level_config.description})",
            f"- 好感度: {affinity_score}/1000",
            f"- 信任度: {trust_score}/100",
            f"- 紧张度: {tension_score}/100",
            f"- 亲密度: {level_config.intimacy_level}/10",
            f"- 你的心情: {current_mood}",
            "",
            f"# 回复风格要求",
            f"- 称呼方式: {', '.join(level_config.addressing_style[:2])}",
            f"- 正式程度: {level_config.response_formality}",
            f"- 表情使用: {level_config.emoji_usage}",
            f"- 禁止使用: {', '.join(response_rule.forbidden_words) if response_rule.forbidden_words else '无限制'}",
            ""
        ]

        # 集成L2：情景记忆（如果提供）
        if recent_memories and len(recent_memories) > 0:
            prompt_parts.extend([
                "# 我们的共同记忆",
                "以下是你和用户之间的相关记忆片段：",
            ])
            for i, memory in enumerate(recent_memories[:5], 1):
                prompt_parts.append(f"{i}. {memory}")
            prompt_parts.append("")

        # 集成L3：语义记忆/用户事实（如果提供）
        if user_facts and len(user_facts) > 0:
            prompt_parts.extend([
                "# 关于用户的已知信息",
            ])
            for key, value in user_facts.items():
                prompt_parts.append(f"- {key}: {value}")
            prompt_parts.append("")

        # 用户当前情感状态（来自LLM分析）
        if emotion_analysis:
            prompt_parts.extend([
                "# 用户当前的情感状态",
                f"- 主要情感: {emotion_analysis.primary_emotion}",
                f"- 情感强度: {emotion_analysis.emotion_intensity:.0%}",
                f"- 意图: {emotion_analysis.user_intent}",
                ""
            ])

        # 行为指导
        prompt_parts.extend([
            "# 你的任务",
            f"请根据以上所有信息，以{companion_name}的身份，用符合当前关系等级的方式回复用户。",
            "要自然、真诚，并体现出你对用户的了解和记忆。",
        ])

        return "\n".join(prompt_parts)

    def _generate_response_guidance(
        self,
        level: str,
        level_config,
        mood: str,
        emotion_analysis: EmotionAnalysis,
        level_changed: bool,
        level_up: bool
    ) -> Dict:
        """生成回复指导"""
        response_rule = get_response_rule(level)

        guidance = {
            "addressing_style": level_config.addressing_style[0] if level_config.addressing_style else "",
            "formality": level_config.response_formality,
            "intimacy_level": level_config.intimacy_level,
            "emoji_usage": level_config.emoji_usage,
            "suggested_emojis": response_rule.allowed_emojis,
            "use_ellipsis": response_rule.use_ellipsis,
            "use_exclamation": response_rule.use_exclamation,
        }

        # 根据情感分析调整
        if emotion_analysis.primary_emotion == "positive":
            guidance["suggested_tone"] = "愉快、热情"
        elif emotion_analysis.primary_emotion == "negative":
            guidance["suggested_tone"] = "温柔、理解、安慰"
        elif emotion_analysis.primary_emotion == "romantic":
            guidance["suggested_tone"] = "甜蜜、心动"
        else:
            guidance["suggested_tone"] = "自然、真诚"

        # 等级变化提示
        if level_changed:
            if level_up:
                guidance["special_message"] = self._get_level_up_message(level)
            else:
                guidance["special_message"] = self._get_level_down_message()

        return guidance

    def _get_level_up_message(self, new_level: str) -> str:
        """等级提升消息"""
        messages = {
            "acquaintance": "看来我们已经不是陌生人了呢~",
            "friend": "感觉我们成为朋友了！",
            "close_friend": "你已经是我的好朋友了！",
            "special": "说实话...你对我来说变得很特别。",
            "romantic": "我对你...好像有了不一样的感觉。",
            "lover": "我想...我们可以在一起了吧？",
        }
        return messages.get(new_level, "感觉我们的关系更近了~")

    def _get_level_down_message(self) -> str:
        """等级降低消息"""
        return "最近感觉我们之间有些疏远...是我做错什么了吗？"


# 全局引擎实例
# 创建一个全局单例
affinity_engine = AffinityEngine()

# 🔥 便捷接口：一键分析并更新好感度
async def analyze_and_update_affinity(
    user_id: str,
    companion_id: int,
    message: str,
    personality_type: str,
    interaction_type: str = "chat"
) -> Dict[str, Any]:
    """
    便捷接口：分析用户消息并自动更新好感度
    
    这是一个高级封装接口，其他服务可以直接调用：
    - 自动获取当前状态
    - 自动分析消息
    - 自动更新数据库
    - 返回分析结果
    
    使用示例：
    result = await analyze_and_update_affinity(
        user_id="user123",
        companion_id=1,
        message="谢谢你的帮助！",
        personality_type="linzixi"
    )
    """
    try:
        # 1. 获取当前状态
        companion_state = await redis_affinity_manager.get_companion_state(user_id, companion_id)
        
        current_affinity_score = companion_state.get("affinity_score", 50) if companion_state else 50
        current_trust_score = companion_state.get("trust_score", 50) if companion_state else 50
        current_tension_score = companion_state.get("tension_score", 0) if companion_state else 0
        current_mood = companion_state.get("current_mood", "neutral") if companion_state else "neutral"
        current_level = companion_state.get("romance_level", "stranger") if companion_state else "stranger"
        
        # 2. 调用完整分析流程
        process_result = await affinity_engine.process_user_message(
            user_message=message,
            current_affinity_score=current_affinity_score,
            current_trust_score=current_trust_score,
            current_tension_score=current_tension_score,
            current_level=current_level,
            current_mood=current_mood,
            companion_name=personality_type,
            user_id=user_id,
            companion_id=companion_id
        )
        
        # 3. 返回简化的结果
        return {
            "success": True,
            "affinity_change": process_result.affinity_change,
            "new_affinity_score": process_result.new_affinity_score,
            "new_level": process_result.new_level,
            "level_changed": process_result.level_changed,
            "emotion": process_result.emotion_analysis.primary_emotion,
            "emotion_intensity": process_result.emotion_analysis.emotion_intensity,
            "is_memorable": process_result.emotion_analysis.is_memorable,
            "enhanced_prompt": process_result.enhanced_system_prompt
        }
        
    except Exception as e:
        logger.error(f"[analyze_and_update_affinity] 处理失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "affinity_change": 0,
            "new_affinity_score": 50,
            "new_level": "stranger",
            "level_changed": False,
            "emotion": "neutral",
            "emotion_intensity": 0.5,
            "is_memorable": False
        }
