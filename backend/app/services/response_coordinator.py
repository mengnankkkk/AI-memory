"""
响应协调器 (Response Coordinator)
双阶段"心流"交互协议的核心调度器

职责：
1. 协调整个双阶段流程的执行
2. 整合情感分析、状态更新、表现生成、提示词构建
3. 管理LLM调用和响应生成
4. 提供统一的API接口
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
import json

from app.services.affinity_engine import affinity_engine, EmotionAnalysis, ProcessResult
from app.services.emotion_expression_generator import emotion_expression_generator, EmotionExpression
from app.services.dynamic_prompt_builder import dynamic_prompt_builder
from app.services.llm.factory import llm_service
from app.services.memory_integration import memory_system

logger = logging.getLogger("response_coordinator")


@dataclass
class CoordinatedResponse:
    """协调后的完整响应"""
    # 最终AI回复
    ai_response: str

    # 阶段1: 情感分析和状态更新
    emotion_analysis: EmotionAnalysis
    process_result: ProcessResult

    # 阶段2: 情感表现和提示词
    emotion_expression: EmotionExpression
    system_prompt: str

    # 元数据
    debug_info: Dict  # 调试信息


class ResponseCoordinator:
    """
    响应协调器

    核心流程：
    1. 【阶段1-情感分析】使用LLM分析用户消息情感和意图
    2. 【阶段1-状态更新】计算并更新好感度、信任度、紧张度
    3. 【阶段1-记忆查询】从记忆系统检索相关记忆
    4. 【阶段2-表现生成】生成详细的情感表现JSON
    5. 【阶段2-提示词构建】构建动态优化的系统提示词
    6. 【阶段2-响应生成】使用LLM生成最终回复
    7. 【后处理】记忆存储、状态持久化
    """

    def __init__(self):
        self.logger = logging.getLogger("response_coordinator")

    async def coordinate_response(
        self,
        # 用户输入
        user_message: str,
        user_id: str,

        # 伙伴信息
        companion_id: int,
        companion_name: str,

        # 当前状态
        current_affinity_score: int,
        current_trust_score: int,
        current_tension_score: int,
        current_level: str,
        current_mood: str = "neutral",

        # 可选参数
        conversation_history: Optional[List[Dict]] = None,
        enable_memory: bool = True,
        special_instructions: Optional[str] = None,
        debug_mode: bool = False

    ) -> CoordinatedResponse:
        """
        协调完整的响应生成流程

        Returns:
            CoordinatedResponse: 包含AI回复和所有中间结果的完整响应
        """
        self.logger.info(
            f"\n{'='*80}\n"
            f"🚀 开始协调响应生成\n"
            f"{'='*80}\n"
            f"用户ID: {user_id} | 伙伴: {companion_name} | 等级: {current_level}\n"
            f"消息: {user_message[:50]}...\n"
            f"{'='*80}"
        )

        debug_info = {
            "stages": {},
            "timings": {},
            "errors": []
        }

        try:
            # ==========================================
            # 阶段1: 情感分析和状态更新
            # ==========================================
            self.logger.info("\n📊 阶段1: 情感分析和状态更新")

            # 1.1 查询记忆（用于情感分析的上下文）
            memories = None
            user_facts = None
            if enable_memory:
                memories, user_facts = await self._query_memory(
                    user_id, companion_id, user_message
                )

            # 1.2 使用AffinityEngine进行情感分析和状态计算
            process_result = await affinity_engine.process_user_message(
                user_message=user_message,
                current_affinity_score=current_affinity_score,
                current_trust_score=current_trust_score,
                current_tension_score=current_tension_score,
                current_level=current_level,
                current_mood=current_mood,
                companion_name=companion_name,
                user_id=user_id,
                companion_id=companion_id,
                recent_memories=memories,
                user_facts=user_facts
            )

            self.logger.info(
                f"✅ 情感分析完成: {process_result.emotion_analysis.primary_emotion} "
                f"(强度:{process_result.emotion_analysis.emotion_intensity:.2f})"
            )
            self.logger.info(
                f"✅ 状态更新: 好感度 {current_affinity_score} → {process_result.new_affinity_score} "
                f"({process_result.affinity_change:+d})"
            )

            debug_info["stages"]["stage1_analysis"] = {
                "emotion": process_result.emotion_analysis.primary_emotion,
                "intensity": process_result.emotion_analysis.emotion_intensity,
                "affinity_change": process_result.affinity_change,
                "new_affinity": process_result.new_affinity_score,
                "level_changed": process_result.level_changed
            }

            # ==========================================
            # 阶段2: 情感表现生成和提示词构建
            # ==========================================
            self.logger.info("\n🎭 阶段2: 情感表现和提示词生成")

            # 2.1 生成情感表现JSON
            emotion_expression = emotion_expression_generator.generate(
                emotion_analysis=process_result.emotion_analysis,
                current_level=process_result.new_level,
                affinity_score=process_result.new_affinity_score,
                trust_score=process_result.new_trust_score,
                tension_score=process_result.new_tension_score,
                mood=current_mood
            )

            self.logger.info(
                f"✅ 情感表现生成: {emotion_expression.emotion_type} "
                f"({emotion_expression.intensity_level}强度)"
            )

            debug_info["stages"]["stage2_expression"] = {
                "emotion_type": emotion_expression.emotion_type,
                "category": emotion_expression.emotion_category,
                "intensity_level": emotion_expression.intensity_level,
                "formality": emotion_expression.verbal_style['formality']
            }

            # 2.2 构建L1工作记忆（当前对话上下文）
            l1_working_memory = self._build_working_memory(conversation_history)

            # 2.3 构建动态系统提示词
            system_prompt = dynamic_prompt_builder.build(
                companion_name=companion_name,
                emotion_expression=emotion_expression,
                emotion_analysis=process_result.emotion_analysis,
                current_level=process_result.new_level,
                affinity_score=process_result.new_affinity_score,
                trust_score=process_result.new_trust_score,
                tension_score=process_result.new_tension_score,
                mood=current_mood,
                l1_working_memory=l1_working_memory,
                l2_episodic_memories=memories,
                l3_semantic_facts=user_facts,
                special_instructions=special_instructions
            )

            self.logger.info(f"✅ 系统提示词构建完成 (长度: {len(system_prompt)} 字符)")

            debug_info["stages"]["stage2_prompt"] = {
                "prompt_length": len(system_prompt),
                "has_memories": bool(memories),
                "has_facts": bool(user_facts)
            }

            # ==========================================
            # 阶段3: LLM生成最终回复
            # ==========================================
            self.logger.info("\n💬 阶段3: LLM生成最终回复")

            # 3.1 构建对话消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            # 如果有对话历史，添加最近几轮（最多3轮）
            if conversation_history:
                recent_history = conversation_history[-6:]  # 最近3轮（6条消息）
                # 在system和user之间插入历史
                messages = [messages[0]] + recent_history + [messages[1]]

            # 3.2 调用LLM
            ai_response = await llm_service.chat_completion(messages)

            self.logger.info(f"✅ AI回复生成完成 (长度: {len(ai_response)} 字符)")

            debug_info["stages"]["stage3_generation"] = {
                "response_length": len(ai_response),
                "message_count": len(messages)
            }

            # ==========================================
            # 阶段4: 后处理（记忆存储、状态持久化）
            # ==========================================
            if enable_memory and process_result.emotion_analysis.is_memorable:
                self.logger.info("\n💾 阶段4: 存储重要记忆")
                await self._store_memory(
                    user_id, companion_id,
                    user_message, ai_response,
                    process_result.emotion_analysis
                )

            # 构建最终响应
            coordinated_response = CoordinatedResponse(
                ai_response=ai_response,
                emotion_analysis=process_result.emotion_analysis,
                process_result=process_result,
                emotion_expression=emotion_expression,
                system_prompt=system_prompt if debug_mode else "[隐藏]",
                debug_info=debug_info if debug_mode else {}
            )

            self.logger.info(
                f"\n{'='*80}\n"
                f"✅ 响应协调完成\n"
                f"{'='*80}"
            )

            return coordinated_response

        except Exception as e:
            self.logger.error(f"❌ 响应协调失败: {e}", exc_info=True)
            debug_info["errors"].append(str(e))

            # 返回降级响应
            return await self._fallback_response(
                user_message, companion_name,
                debug_info, str(e)
            )

    async def _query_memory(
        self,
        user_id: str,
        companion_id: int,
        user_message: str
    ) -> Tuple[Optional[List[str]], Optional[Dict]]:
        """
        从记忆系统查询相关信息

        Returns:
            (memories, facts): (L2情景记忆列表, L3用户事实字典)
        """
        try:
            # 查询相关记忆（L2）
            memories = await memory_system.get_recent_memories(
                user_id=user_id,
                companion_id=companion_id,
                query=user_message,
                limit=5
            )

            # 获取用户事实（L3）
            user_facts = await memory_system.get_user_facts(
                user_id=user_id,
                companion_id=companion_id
            )

            self.logger.info(
                f"📚 记忆查询: {len(memories) if memories else 0} 条记忆, "
                f"{len(user_facts) if user_facts else 0} 个事实"
            )

            return memories, user_facts

        except Exception as e:
            self.logger.warning(f"记忆查询失败: {e}")
            return None, None

    async def _store_memory(
        self,
        user_id: str,
        companion_id: int,
        user_message: str,
        ai_response: str,
        emotion_analysis: EmotionAnalysis
    ):
        """存储重要记忆"""
        try:
            await memory_system.save_memory(
                user_id=user_id,
                companion_id=companion_id,
                memory_text=f"用户: {user_message}\nAI: {ai_response}",
                memory_type="conversation"
            )
            self.logger.info("💾 记忆存储成功")
        except Exception as e:
            self.logger.warning(f"记忆存储失败: {e}")

    def _build_working_memory(
        self,
        conversation_history: Optional[List[Dict]]
    ) -> Optional[str]:
        """
        构建L1工作记忆（当前对话上下文摘要）

        Args:
            conversation_history: 对话历史 [{"role": "user/assistant", "content": "..."}]

        Returns:
            str: 工作记忆摘要
        """
        if not conversation_history or len(conversation_history) == 0:
            return None

        # 获取最近的对话（最多5轮，10条消息）
        recent = conversation_history[-10:]

        # 构建简洁的上下文摘要
        context_lines = []
        for msg in recent:
            role = "用户" if msg["role"] == "user" else "你"
            content = msg["content"][:100]  # 限制长度
            context_lines.append(f"{role}: {content}")

        return "最近对话:\n" + "\n".join(context_lines)

    async def _fallback_response(
        self,
        user_message: str,
        companion_name: str,
        debug_info: Dict,
        error_message: str
    ) -> CoordinatedResponse:
        """生成降级响应（当主流程失败时）"""
        self.logger.warning("⚠️ 使用降级响应")

        # 使用简单的LLM调用生成回复
        try:
            simple_prompt = f"你是{companion_name}。请简短、友好地回复用户的消息。"
            messages = [
                {"role": "system", "content": simple_prompt},
                {"role": "user", "content": user_message}
            ]
            ai_response = await llm_service.chat_completion(messages)
        except:
            ai_response = "抱歉，我现在有点不在状态...能再说一遍吗？"

        # 构建最小化的响应对象
        from app.services.affinity_engine import EmotionAnalysis, ProcessResult
        from app.services.emotion_expression_generator import EmotionExpression

        minimal_emotion = EmotionAnalysis(
            primary_emotion="neutral",
            emotion_intensity=0.3,
            detected_emotions=[],
            user_intent="unknown",
            is_appropriate=True,
            violation_reason="",
            suggested_affinity_change=0,
            suggested_trust_change=0,
            suggested_tension_change=0,
            key_points=[],
            is_memorable=False
        )

        minimal_result = ProcessResult(
            emotion_analysis=minimal_emotion,
            affinity_change=0,
            trust_change=0,
            tension_change=0,
            new_affinity_score=0,
            new_trust_score=0,
            new_tension_score=0,
            new_level="stranger",
            new_level_name="陌生",
            level_changed=False,
            level_up=False,
            level_down=False,
            level_change_message="",
            response_guidance={},
            enhanced_system_prompt="",
            protection_warnings=[],
            protection_reason="",
            trend="",
            recovery_suggestion=""
        )

        minimal_expression = EmotionExpression(
            emotion_type="calm",
            emotion_category="neutral",
            intensity=0.3,
            intensity_level="low",
            verbal_style={},
            tone_guidance=[],
            suggested_phrases=[],
            punctuation_guide=[],
            body_language=[],
            facial_expression=[],
            voice_characteristics=[],
            response_structure={},
            opening_suggestions=[],
            closing_suggestions=[],
            affinity_level="stranger",
            intimacy_constraints={},
            user_intent="unknown",
            is_appropriate=True,
            adaptation_notes=[]
        )

        debug_info["errors"].append(f"Fallback activated: {error_message}")

        return CoordinatedResponse(
            ai_response=ai_response,
            emotion_analysis=minimal_emotion,
            process_result=minimal_result,
            emotion_expression=minimal_expression,
            system_prompt="[降级模式]",
            debug_info=debug_info
        )

    def serialize_response(self, response: CoordinatedResponse) -> Dict:
        """将响应序列化为JSON可序列化的字典"""
        return {
            "ai_response": response.ai_response,
            "emotion_analysis": asdict(response.emotion_analysis),
            "process_result": asdict(response.process_result),
            "emotion_expression": asdict(response.emotion_expression),
            "system_prompt": response.system_prompt,
            "debug_info": response.debug_info
        }


# 全局实例
response_coordinator = ResponseCoordinator()
