"""
AI情感计算引擎 (Affinity Engine)
使用两阶段LLM调用架构，实现真正的AI级别情感理解
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json
import logging

from app.services.llm.factory import llm_service
from app.config.affinity_levels import (
    get_level_by_score,
    get_level_config,
    AFFINITY_LEVELS
)
from app.config.response_rules import get_response_rule
from app.services.affinity_protector import AffinityProtector

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
            from app.config.affinity_levels import LEVEL_ORDER
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
affinity_engine = AffinityEngine()
