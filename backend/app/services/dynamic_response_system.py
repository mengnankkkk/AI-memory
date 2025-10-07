"""
动态回复系统 - 完整实现
整合好感度管理、内容检测、回复生成等功能
"""
from typing import Dict, List, Optional, Tuple
import random
import logging

from app.config.affinity_levels import (
    get_level_by_score,
    get_level_config,
    AFFINITY_LEVELS,
    LEVEL_ORDER
)
from app.config.response_rules import (
    get_response_rule,
    RESPONSE_MODIFIERS,
    TONE_CONVERSION
)
from app.services.content_detector import ContentDetector, DetectionResult
from app.services.affinity_protector import AffinityProtector, ProtectionResult

logger = logging.getLogger("dynamic_response_system")


class DynamicResponseSystem:
    """动态回复系统主类"""

    def __init__(self):
        self.detector = ContentDetector()
        self.protector = AffinityProtector()

    def process_user_message(
        self,
        user_message: str,
        current_affinity_score: int,
        user_id: str,
        companion_id: int,
        current_mood: str = "平静"
    ) -> Dict:
        """
        处理用户消息的完整流程

        Args:
            user_message: 用户消息内容
            current_affinity_score: 当前好感度分数
            user_id: 用户ID
            companion_id: 伙伴ID
            current_mood: 当前心情

        Returns:
            包含所有处理结果的字典
        """
        # 1. 获取当前等级
        current_level = get_level_by_score(current_affinity_score)
        level_config = get_level_config(current_level)

        logger.info(f"处理消息 - 用户:{user_id}, 当前等级:{level_config.name}, 分数:{current_affinity_score}")

        # 2. 内容检测
        detection_result = self.detector.detect(user_message, current_level)

        logger.info(
            f"检测结果 - 合适:{detection_result.is_appropriate}, "
            f"原始变化:{detection_result.affinity_change}, "
            f"情感:{detection_result.detected_emotions}"
        )

        # 3. 应用保护机制
        protection_result = self.protector.protect_and_adjust(
            current_affinity_score,
            detection_result.affinity_change,
            reason=f"情感:{detection_result.detected_emotions}"
        )

        logger.info(
            f"保护结果 - 调整后变化:{protection_result.adjusted_change}, "
            f"保护原因:{protection_result.protection_reason}"
        )

        # 4. 计算新分数和等级
        new_affinity_score = current_affinity_score + protection_result.adjusted_change
        new_level = get_level_by_score(new_affinity_score)
        new_level_config = get_level_config(new_level)

        # 5. 检测等级变化
        level_changed = current_level != new_level
        level_up = False
        level_down = False

        if level_changed:
            current_index = LEVEL_ORDER.index(current_level)
            new_index = LEVEL_ORDER.index(new_level)
            level_up = new_index > current_index
            level_down = new_index < current_index

        # 6. 生成回复指导信息
        response_guidance = self._generate_response_guidance(
            new_level,
            new_level_config,
            current_mood,
            detection_result,
            level_changed,
            level_up
        )

        # 7. 返回完整结果
        return {
            "detection": {
                "is_appropriate": detection_result.is_appropriate,
                "violation_type": detection_result.violation_type,
                "violation_severity": detection_result.violation_severity,
                "detected_emotions": detection_result.detected_emotions,
                "detected_keywords": detection_result.detected_keywords,
                "suggestion": detection_result.suggestion,
            },
            "affinity_change": {
                "original_change": protection_result.original_change,
                "adjusted_change": protection_result.adjusted_change,
                "applied_rate": protection_result.applied_rate,
                "protection_reason": protection_result.protection_reason,
                "warnings": protection_result.warnings,
            },
            "affinity_state": {
                "before_score": current_affinity_score,
                "after_score": new_affinity_score,
                "before_level": level_config.name,
                "after_level": new_level_config.name,
                "level_changed": level_changed,
                "level_up": level_up,
                "level_down": level_down,
            },
            "response_guidance": response_guidance,
            "history_summary": self.protector.get_history_summary(),
            "trend": self.protector.get_recent_trend(),
            "recovery_suggestion": self.protector.suggest_recovery_action(new_affinity_score)
        }

    def _generate_response_guidance(
        self,
        level: str,
        level_config,
        mood: str,
        detection_result: DetectionResult,
        level_changed: bool,
        level_up: bool
    ) -> Dict:
        """生成回复指导信息"""
        response_rule = get_response_rule(level)

        # 基础回复指导
        guidance = {
            "addressing_style": random.choice(level_config.addressing_style),
            "tone_keywords": response_rule.sentence_endings,
            "emoji_usage": level_config.emoji_usage,
            "suggested_emojis": response_rule.allowed_emojis,
            "emoji_frequency": response_rule.emoji_frequency,
            "formality": level_config.response_formality,
            "intimacy_level": level_config.intimacy_level,
            "message_length": response_rule.message_length_preference,
            "use_ellipsis": response_rule.use_ellipsis,
            "use_exclamation": response_rule.use_exclamation,
        }

        # 根据情感调整建议
        if "positive_joy" in detection_result.detected_emotions:
            guidance["mood_adjustment"] = "happy"
            guidance["suggested_tone"] = "愉快、热情"
        elif "negative_sadness" in detection_result.detected_emotions:
            guidance["mood_adjustment"] = "comforting"
            guidance["suggested_tone"] = "温柔、安慰"
        elif "negative_anger" in detection_result.detected_emotions:
            guidance["mood_adjustment"] = "calm"
            guidance["suggested_tone"] = "平静、理解"
        else:
            guidance["mood_adjustment"] = "normal"
            guidance["suggested_tone"] = "自然、真诚"

        # 等级变化特殊指导
        if level_changed:
            if level_up:
                guidance["special_message"] = self._get_level_up_message(level)
                guidance["celebrate"] = True
            else:
                guidance["special_message"] = self._get_level_down_message(level)
                guidance["comfort"] = True

        # 选择合适的回复模板
        if "positive_compliment" in detection_result.detected_emotions:
            guidance["suggested_response"] = random.choice(response_rule.compliment_responses)
        elif "greeting" in detection_result.detected_keywords:
            guidance["suggested_response"] = random.choice(response_rule.greeting_templates)
        else:
            guidance["suggested_response"] = random.choice(response_rule.response_templates)

        # 话题建议
        guidance["topic_suggestions"] = response_rule.topic_suggestions

        return guidance

    def _get_level_up_message(self, new_level: str) -> str:
        """获取升级提示消息"""
        messages = {
            "acquaintance": "看来我们已经不是陌生人了呢~",
            "friend": "感觉我们成为朋友了!",
            "close_friend": "你已经是我的好朋友了!",
            "special": "说实话...你对我来说变得很特别。",
            "romantic": "我对你...好像有了不一样的感觉。",
            "lover": "我想...我们可以在一起了吧?",
        }
        return messages.get(new_level, "感觉我们的关系更近了~")

    def _get_level_down_message(self, new_level: str) -> str:
        """获取降级提示消息"""
        return "最近感觉我们之间有些疏远...是我做错什么了吗?"

    def generate_ai_response(
        self,
        base_response: str,
        response_guidance: Dict
    ) -> str:
        """
        根据指导信息调整AI回复

        Args:
            base_response: LLM生成的原始回复
            response_guidance: 回复指导信息

        Returns:
            调整后的回复
        """
        adjusted_response = base_response

        # 1. 添加称呼
        addressing = response_guidance.get("addressing_style", "")
        if addressing and not any(addr in adjusted_response for addr in ["亲爱的", "宝贝", "你"]):
            if response_guidance.get("intimacy_level", 1) >= 8:
                adjusted_response = f"{addressing}，{adjusted_response}"

        # 2. 调整语气词
        if response_guidance.get("use_ellipsis"):
            # 适度添加省略号
            if random.random() < 0.3 and "..." not in adjusted_response:
                adjusted_response = adjusted_response.replace("。", "...")

        if response_guidance.get("use_exclamation"):
            # 积极情感时增加感叹号
            if response_guidance.get("mood_adjustment") == "happy":
                adjusted_response = adjusted_response.replace("。", "!")

        # 3. 添加表情符号
        emoji_freq = response_guidance.get("emoji_frequency", 0)
        if emoji_freq > 0 and random.random() < emoji_freq:
            emojis = response_guidance.get("suggested_emojis", [])
            if emojis:
                emoji = random.choice(emojis)
                adjusted_response = f"{adjusted_response} {emoji}"

        # 4. 添加特殊消息(等级变化时)
        special_message = response_guidance.get("special_message")
        if special_message:
            adjusted_response = f"{adjusted_response}\n\n{special_message}"

        # 5. 长度控制
        length_pref = response_guidance.get("message_length", "medium")
        if length_pref == "short" and len(adjusted_response) > 50:
            # 截断过长的回复
            adjusted_response = adjusted_response[:50] + "..."
        elif length_pref == "long" and len(adjusted_response) < 30:
            # 短回复添加填充
            fillers = ["嗯嗯", "说真的", "其实"]
            filler = random.choice(fillers)
            adjusted_response = f"{filler}，{adjusted_response}"

        return adjusted_response

    def get_system_prompt_enhancement(
        self,
        base_system_prompt: str,
        level: str,
        mood: str,
        affinity_score: int
    ) -> str:
        """
        增强系统提示词

        为LLM提供详细的角色状态和行为指导
        """
        level_config = get_level_config(level)
        response_rule = get_response_rule(level)

        enhancement = f"""
{base_system_prompt}

【当前关系状态】
- 关系等级: {level_config.name} ({level_config.description})
- 好感度分数: {affinity_score}/1000
- 亲密度: {level_config.intimacy_level}/10
- 当前心情: {mood}

【回复风格指导】
- 称呼方式: {', '.join(level_config.addressing_style[:2])}
- 语气正式度: {level_config.response_formality}
- 表情使用: {level_config.emoji_usage}
- 建议语气词: {', '.join(response_rule.sentence_endings[:3])}

【行为规范】
{level_config.description}

请严格根据当前关系状态调整回复风格,保持角色一致性。
不要使用以下禁忌词: {', '.join(response_rule.forbidden_words) if response_rule.forbidden_words else '无'}
可以谈论的话题: {', '.join(response_rule.topic_suggestions[:3])}
"""
        return enhancement


# 全局系统实例
dynamic_response_system = DynamicResponseSystem()
