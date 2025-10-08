"""
情感表现JSON生成器 (Emotion Expression Generator)
双阶段"心流"交互协议 - 阶段1核心组件

职责：
1. 基于情感分析结果生成详细的情感表现JSON
2. 融合亲密度等级、情感类型、情感强度等多维度信息
3. 为LLM提供精确的情感表达指导
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import random
import logging

from app.config.emotion_templates import (
    get_emotion_template,
    get_intensity_level,
    EmotionTemplate
)
from app.config.affinity_levels import get_level_config
from app.services.affinity_engine import EmotionAnalysis

logger = logging.getLogger("emotion_expression")


@dataclass
class EmotionExpression:
    """情感表现JSON结构"""
    # 核心情感信息
    emotion_type: str  # 情感类型
    emotion_category: str  # 情感类别: positive/romantic/negative/neutral
    intensity: float  # 情感强度 0-1
    intensity_level: str  # 强度等级: low/medium/high

    # 语言表达
    verbal_style: Dict[str, any]  # 语言风格
    tone_guidance: List[str]  # 语调指导
    suggested_phrases: List[str]  # 建议的表达短语
    punctuation_guide: List[str]  # 标点符号指导

    # 非语言表现
    body_language: List[str]  # 肢体语言
    facial_expression: List[str]  # 面部表情
    voice_characteristics: List[str]  # 声音特征

    # 回复结构指导
    response_structure: Dict[str, any]  # 回复结构
    opening_suggestions: List[str]  # 开场建议
    closing_suggestions: List[str]  # 结尾建议

    # 亲密度适配
    affinity_level: str  # 当前亲密度等级
    intimacy_constraints: Dict[str, any]  # 亲密度约束

    # 情境感知
    user_intent: str  # 用户意图
    is_appropriate: bool  # 是否适合当前关系
    adaptation_notes: List[str]  # 适配注意事项


class EmotionExpressionGenerator:
    """情感表现JSON生成器"""

    def __init__(self):
        self.logger = logging.getLogger("emotion_expression")

    def generate(
        self,
        emotion_analysis: EmotionAnalysis,
        current_level: str,
        affinity_score: int,
        trust_score: int,
        tension_score: int,
        mood: str
    ) -> EmotionExpression:
        """
        生成情感表现JSON

        Args:
            emotion_analysis: 情感分析结果
            current_level: 当前亲密度等级
            affinity_score: 好感度分数
            trust_score: 信任度
            tension_score: 紧张度
            mood: 当前心情

        Returns:
            EmotionExpression: 详细的情感表现JSON
        """
        self.logger.info(
            f"[EmotionExpression] 生成情感表现 - "
            f"情感:{emotion_analysis.primary_emotion}, "
            f"强度:{emotion_analysis.emotion_intensity:.2f}, "
            f"等级:{current_level}"
        )

        # 确定情感类别
        emotion_category = self._categorize_emotion(emotion_analysis.primary_emotion)

        # 选择主要情感（如果有多个detected_emotions，选择最匹配的）
        primary_emotion_type = self._select_primary_emotion_type(
            emotion_analysis.detected_emotions,
            emotion_analysis.primary_emotion
        )

        # 获取情感模板
        emotion_template = get_emotion_template(
            primary_emotion_type,
            emotion_analysis.emotion_intensity,
            emotion_category
        )

        # 获取亲密度配置
        level_config = get_level_config(current_level)

        # 构建语言风格
        verbal_style = self._build_verbal_style(
            emotion_template,
            level_config,
            emotion_analysis.emotion_intensity
        )

        # 构建回复结构指导
        response_structure = self._build_response_structure(
            emotion_template,
            emotion_analysis.user_intent,
            level_config
        )

        # 构建亲密度约束
        intimacy_constraints = self._build_intimacy_constraints(
            level_config,
            emotion_analysis.is_appropriate,
            emotion_analysis.violation_reason
        )

        # 生成适配注意事项
        adaptation_notes = self._generate_adaptation_notes(
            emotion_analysis,
            level_config,
            trust_score,
            tension_score,
            mood
        )

        return EmotionExpression(
            emotion_type=primary_emotion_type,
            emotion_category=emotion_category,
            intensity=emotion_analysis.emotion_intensity,
            intensity_level=get_intensity_level(emotion_analysis.emotion_intensity),
            verbal_style=verbal_style,
            tone_guidance=emotion_template.tone_modifiers,
            suggested_phrases=self._select_random_subset(emotion_template.verbal_expressions, 3),
            punctuation_guide=emotion_template.punctuation_patterns,
            body_language=emotion_template.body_language,
            facial_expression=emotion_template.facial_expressions,
            voice_characteristics=emotion_template.voice_characteristics,
            response_structure=response_structure,
            opening_suggestions=emotion_template.opening_phrases,
            closing_suggestions=emotion_template.closing_phrases,
            affinity_level=current_level,
            intimacy_constraints=intimacy_constraints,
            user_intent=emotion_analysis.user_intent,
            is_appropriate=emotion_analysis.is_appropriate,
            adaptation_notes=adaptation_notes
        )

    def _categorize_emotion(self, primary_emotion: str) -> str:
        """确定情感类别"""
        if primary_emotion == "positive":
            return "positive"
        elif primary_emotion == "negative":
            return "negative"
        elif primary_emotion == "romantic":
            return "romantic"
        else:
            return "neutral"

    def _select_primary_emotion_type(
        self,
        detected_emotions: List[str],
        primary_emotion: str
    ) -> str:
        """从检测到的具体情感中选择主要情感类型"""
        if not detected_emotions:
            # 降级到主要情感类别
            return "calm" if primary_emotion == "neutral" else "joy"

        # 返回第一个检测到的具体情感
        return detected_emotions[0]

    def _build_verbal_style(
        self,
        template: EmotionTemplate,
        level_config,
        intensity: float
    ) -> Dict:
        """构建语言风格指导"""
        return {
            "formality": level_config.response_formality,
            "tone": template.tone_modifiers[0] if template.tone_modifiers else "自然",
            "emotion_intensity": intensity,
            "addressing": level_config.addressing_style[0] if level_config.addressing_style else "你",
            "emoji_usage": level_config.emoji_usage,
            "recommended_emojis": self._filter_emojis_by_emotion(
                template.punctuation_patterns
            )
        }

    def _filter_emojis_by_emotion(self, punctuation_patterns: List[str]) -> List[str]:
        """从标点符号模式中提取emoji"""
        emojis = []
        for pattern in punctuation_patterns:
            # 检查是否包含emoji（简单判断：非ASCII字符且长度为1）
            if len(pattern) == 1 and ord(pattern) > 127:
                emojis.append(pattern)
            # 或者包含特定emoji标记
            elif any(emoji in pattern for emoji in ["😊", "💕", "😢", "🎉", "✨", "💖", "😭", "😔", "🤔", "💔", "🙏", "😘", "💗", "❤️", "💭", "🎊", "💫"]):
                for char in pattern:
                    if ord(char) > 127:
                        emojis.append(char)
        return emojis

    def _build_response_structure(
        self,
        template: EmotionTemplate,
        user_intent: str,
        level_config
    ) -> Dict:
        """构建回复结构指导"""
        return {
            "pattern": template.response_patterns[0] if template.response_patterns else "自然回应",
            "user_intent": user_intent,
            "length_guidance": self._suggest_response_length(user_intent, level_config.intimacy_level),
            "flow": self._suggest_response_flow(user_intent),
            "personalization": self._suggest_personalization(level_config.intimacy_level)
        }

    def _suggest_response_length(self, user_intent: str, intimacy_level: int) -> str:
        """建议回复长度"""
        if user_intent in ["question", "request"]:
            return "medium_to_long"  # 中长回复，给予详细答案
        elif user_intent in ["greeting", "compliment"]:
            return "short_to_medium"  # 短到中等，简洁友好
        elif user_intent in ["sharing", "confession"]:
            if intimacy_level >= 7:
                return "long"  # 长回复，深入交流
            else:
                return "medium"
        else:
            return "medium"

    def _suggest_response_flow(self, user_intent: str) -> List[str]:
        """建议回复流程"""
        flow_templates = {
            "greeting": ["回应问候", "简短寒暄"],
            "question": ["理解问题", "给出答案", "适当延伸"],
            "sharing": ["表达理解", "回应情感", "分享相关经历/观点"],
            "compliment": ["表达感谢", "适度回应", "转移话题或深化交流"],
            "complaint": ["表达理解", "提供安慰", "给予建议"],
            "request": ["确认需求", "提供帮助", "后续关怀"],
            "confession": ["接收情感", "真诚回应", "明确态度"]
        }
        return flow_templates.get(user_intent, ["理解意图", "自然回应"])

    def _suggest_personalization(self, intimacy_level: int) -> Dict:
        """建议个性化程度"""
        if intimacy_level <= 3:
            return {
                "level": "low",
                "techniques": ["使用基本礼貌用语", "保持适当距离"]
            }
        elif intimacy_level <= 6:
            return {
                "level": "medium",
                "techniques": ["称呼更亲切", "分享一些个人感受", "适度幽默"]
            }
        else:
            return {
                "level": "high",
                "techniques": ["使用昵称", "深度情感表达", "回忆共同记忆", "表达关切"]
            }

    def _build_intimacy_constraints(
        self,
        level_config,
        is_appropriate: bool,
        violation_reason: str
    ) -> Dict:
        """构建亲密度约束"""
        return {
            "current_level": level_config.name,
            "intimacy_level": level_config.intimacy_level,
            "is_appropriate": is_appropriate,
            "violation_reason": violation_reason,
            "boundaries": self._define_boundaries(level_config.intimacy_level),
            "allowed_topics": self._define_allowed_topics(level_config.intimacy_level),
            "forbidden_behaviors": self._define_forbidden_behaviors(level_config.intimacy_level)
        }

    def _define_boundaries(self, intimacy_level: int) -> List[str]:
        """定义当前等级的边界"""
        if intimacy_level <= 2:
            return [
                "保持礼貌距离",
                "避免过于私人的话题",
                "不使用亲昵称呼",
                "不表达浪漫情感"
            ]
        elif intimacy_level <= 5:
            return [
                "可以适度友好",
                "避免过度亲密",
                "不表达浪漫情感",
                "保持友谊边界"
            ]
        elif intimacy_level <= 7:
            return [
                "可以表达特别感受",
                "避免过激表达",
                "谨慎处理浪漫暗示"
            ]
        else:
            return [
                "可以表达浪漫情感",
                "保持真诚和尊重",
                "避免过度依赖"
            ]

    def _define_allowed_topics(self, intimacy_level: int) -> List[str]:
        """定义允许的话题"""
        base_topics = ["日常生活", "兴趣爱好", "工作学习"]

        if intimacy_level >= 4:
            base_topics.extend(["个人感受", "生活困扰", "未来计划"])

        if intimacy_level >= 7:
            base_topics.extend(["深层情感", "关系讨论", "浪漫话题"])

        return base_topics

    def _define_forbidden_behaviors(self, intimacy_level: int) -> List[str]:
        """定义禁止的行为"""
        forbidden = []

        if intimacy_level < 7:
            forbidden.extend([
                "表达强烈爱意",
                "使用过于亲密的称呼",
                "暗示身体接触"
            ])

        if intimacy_level < 5:
            forbidden.extend([
                "分享过于私密的信息",
                "表达特殊好感"
            ])

        if intimacy_level < 3:
            forbidden.extend([
                "过度关心对方私生活",
                "使用非正式语言"
            ])

        return forbidden

    def _generate_adaptation_notes(
        self,
        emotion_analysis: EmotionAnalysis,
        level_config,
        trust_score: int,
        tension_score: int,
        mood: str
    ) -> List[str]:
        """生成适配注意事项"""
        notes = []

        # 基于情感分析
        if not emotion_analysis.is_appropriate:
            notes.append(f"⚠️ 用户消息可能超出当前关系边界: {emotion_analysis.violation_reason}")

        # 基于信任度
        if trust_score < 30:
            notes.append("💡 信任度较低，回复应更加谨慎和真诚")
        elif trust_score > 80:
            notes.append("💡 信任度高，可以更加坦诚和深入交流")

        # 基于紧张度
        if tension_score > 60:
            notes.append("⚠️ 紧张度高，需要缓和气氛，避免冲突")
        elif tension_score < 20:
            notes.append("💡 氛围轻松，可以更加活泼和幽默")

        # 基于心情
        if mood in ["happy", "excited"]:
            notes.append("💡 保持积极氛围，可以更加热情")
        elif mood in ["sad", "depressed"]:
            notes.append("💡 提供情感支持，语气温柔体贴")

        # 基于用户意图
        if emotion_analysis.user_intent == "confession":
            notes.append("💖 用户可能在表达特殊情感，需要认真对待")
        elif emotion_analysis.user_intent == "complaint":
            notes.append("💙 用户在倾诉，提供理解和支持")

        return notes

    def _select_random_subset(self, items: List, max_count: int) -> List:
        """随机选择子集"""
        if not items:
            return []
        if len(items) <= max_count:
            return items
        return random.sample(items, max_count)

    def to_json(self, expression: EmotionExpression) -> Dict:
        """转换为JSON字典"""
        return asdict(expression)


# 全局实例
emotion_expression_generator = EmotionExpressionGenerator()
