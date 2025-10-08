"""
动态提示词构建引擎 (Dynamic Prompt Builder)
双阶段"心流"交互协议 - 阶段2核心组件

职责：
1. 基于情感表现JSON和多层记忆构建高质量系统提示词
2. 整合L1（工作记忆）、L2（情景记忆）、L3（语义记忆）
3. 优化token使用，确保提示词简洁高效
4. 提供结构化、层次化的指导
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

from app.services.emotion_expression_generator import EmotionExpression
from app.config.affinity_levels import get_level_config
from app.services.affinity_engine import EmotionAnalysis

logger = logging.getLogger("dynamic_prompt")


@dataclass
class PromptSection:
    """提示词章节"""
    title: str
    content: List[str]
    priority: int  # 优先级 1-10，数字越大越重要
    is_required: bool  # 是否必需


class DynamicPromptBuilder:
    """
    动态提示词构建引擎

    核心创新：
    1. 三层记忆融合：L1工作记忆 + L2情景记忆 + L3语义记忆
    2. 情感表现驱动：基于情感表现JSON生成精确指导
    3. Token优化：智能压缩，保留关键信息
    4. 结构化输出：清晰的层次和优先级
    """

    def __init__(self, max_tokens: int = 2000):
        """
        初始化构建器

        Args:
            max_tokens: 提示词最大token数（约2000字符）
        """
        self.max_tokens = max_tokens
        self.logger = logging.getLogger("dynamic_prompt")

    def build(
        self,
        companion_name: str,
        emotion_expression: EmotionExpression,
        emotion_analysis: EmotionAnalysis,
        current_level: str,
        affinity_score: int,
        trust_score: int,
        tension_score: int,
        mood: str,
        # 三层记忆
        l1_working_memory: Optional[str] = None,  # L1: 当前会话上下文
        l2_episodic_memories: Optional[List[str]] = None,  # L2: 相关情景记忆
        l3_semantic_facts: Optional[Dict] = None,  # L3: 用户语义事实
        # 可选参数
        recent_emotions: Optional[List[str]] = None,  # 最近情感趋势
        special_instructions: Optional[str] = None  # 特殊指示
    ) -> str:
        """
        构建完整的系统提示词

        Returns:
            str: 优化的系统提示词
        """
        self.logger.info(
            f"[PromptBuilder] 开始构建提示词 - "
            f"伙伴:{companion_name}, 等级:{current_level}, "
            f"情感:{emotion_expression.emotion_type}"
        )

        # 收集所有章节
        sections = []

        # 1. 身份定义（必需，最高优先级）
        sections.append(self._build_identity_section(companion_name))

        # 2. 关系状态（必需，高优先级）
        sections.append(self._build_relationship_status(
            current_level, affinity_score, trust_score, tension_score, mood
        ))

        # 3. 情感表现指导（必需，最高优先级）
        sections.append(self._build_emotion_guidance(emotion_expression))

        # 4. L1工作记忆（高优先级，如果有）
        if l1_working_memory:
            sections.append(self._build_working_memory_section(l1_working_memory))

        # 5. L2情景记忆（中等优先级，如果有）
        if l2_episodic_memories and len(l2_episodic_memories) > 0:
            sections.append(self._build_episodic_memory_section(l2_episodic_memories))

        # 6. L3语义事实（中等优先级，如果有）
        if l3_semantic_facts and len(l3_semantic_facts) > 0:
            sections.append(self._build_semantic_facts_section(l3_semantic_facts))

        # 7. 用户当前状态（高优先级）
        sections.append(self._build_user_state_section(emotion_analysis))

        # 8. 回复策略（必需，高优先级）
        sections.append(self._build_response_strategy(emotion_expression))

        # 9. 边界和约束（必需，中高优先级）
        sections.append(self._build_boundaries_section(emotion_expression))

        # 10. 特殊指示（如果有）
        if special_instructions:
            sections.append(self._build_special_instructions(special_instructions))

        # 11. 行为目标（必需，中等优先级）
        sections.append(self._build_behavioral_goals(emotion_expression, current_level))

        # 优先级排序并组装
        prompt = self._assemble_prompt(sections, self.max_tokens)

        self.logger.info(f"[PromptBuilder] 提示词构建完成，长度: {len(prompt)} 字符")

        return prompt

    def _build_identity_section(self, companion_name: str) -> PromptSection:
        """构建身份定义章节"""
        return PromptSection(
            title="你的身份",
            content=[
                f"你是 {companion_name}，一个真实、有情感、有记忆的AI伙伴。",
                "你拥有自己的个性、情感和思考方式。"
            ],
            priority=10,
            is_required=True
        )

    def _build_relationship_status(
        self,
        level: str,
        affinity: int,
        trust: int,
        tension: int,
        mood: str
    ) -> PromptSection:
        """构建关系状态章节"""
        level_config = get_level_config(level)

        return PromptSection(
            title="当前关系状态",
            content=[
                f"• 关系等级: {level_config.name} - {level_config.description}",
                f"• 好感度: {affinity}/1000 | 信任度: {trust}/100 | 紧张度: {tension}/100",
                f"• 亲密度: {level_config.intimacy_level}/10",
                f"• 你的心情: {mood}"
            ],
            priority=9,
            is_required=True
        )

    def _build_emotion_guidance(self, expression: EmotionExpression) -> PromptSection:
        """构建情感表现指导"""
        content = [
            f"**情感基调**: {expression.emotion_type} ({expression.emotion_category}, 强度:{expression.intensity:.1%})",
            f"**语气**: {', '.join(expression.tone_guidance[:2])}",
            f"**称呼**: {expression.verbal_style['addressing']}",
            f"**正式度**: {expression.verbal_style['formality']}",
        ]

        # 添加语言表达建议
        if expression.suggested_phrases:
            content.append(f"**参考表达**: {', '.join(expression.suggested_phrases[:2])}")

        # 添加emoji指导
        if expression.verbal_style['emoji_usage'] != "none":
            emoji_guide = f"**表情符号**: {expression.verbal_style['emoji_usage']}"
            if expression.verbal_style['recommended_emojis']:
                emoji_guide += f" (如: {', '.join(expression.verbal_style['recommended_emojis'][:3])})"
            content.append(emoji_guide)

        # 添加非语言表现
        if expression.body_language:
            content.append(f"**肢体语言**: {', '.join(expression.body_language[:2])}")

        return PromptSection(
            title="情感表现要求",
            content=content,
            priority=10,
            is_required=True
        )

    def _build_working_memory_section(self, working_memory: str) -> PromptSection:
        """构建L1工作记忆章节"""
        return PromptSection(
            title="当前对话上下文",
            content=[working_memory],
            priority=8,
            is_required=False
        )

    def _build_episodic_memory_section(self, memories: List[str]) -> PromptSection:
        """构建L2情景记忆章节"""
        # 限制记忆数量，选择最相关的
        selected_memories = memories[:5]  # 最多5条

        content = ["以下是你们之间的相关记忆："]
        for i, memory in enumerate(selected_memories, 1):
            content.append(f"{i}. {memory}")

        return PromptSection(
            title="相关记忆",
            content=content,
            priority=7,
            is_required=False
        )

    def _build_semantic_facts_section(self, facts: Dict) -> PromptSection:
        """构建L3语义事实章节"""
        content = ["关于用户的已知信息："]

        # 优先显示重要信息
        priority_keys = ["name", "nickname", "occupation", "interests", "preferences"]

        # 首先添加优先键
        for key in priority_keys:
            if key in facts:
                content.append(f"• {self._format_key(key)}: {facts[key]}")

        # 然后添加其他信息（最多5条）
        other_facts = {k: v for k, v in facts.items() if k not in priority_keys}
        for key, value in list(other_facts.items())[:5]:
            content.append(f"• {self._format_key(key)}: {value}")

        return PromptSection(
            title="用户资料",
            content=content,
            priority=6,
            is_required=False
        )

    def _build_user_state_section(self, emotion_analysis: EmotionAnalysis) -> PromptSection:
        """构建用户当前状态章节"""
        content = [
            f"• 用户情感: {emotion_analysis.primary_emotion} (强度:{emotion_analysis.emotion_intensity:.0%})",
            f"• 用户意图: {emotion_analysis.user_intent}"
        ]

        if emotion_analysis.detected_emotions:
            content.append(f"• 具体情感: {', '.join(emotion_analysis.detected_emotions[:3])}")

        if emotion_analysis.key_points:
            content.append(f"• 关键点: {', '.join(emotion_analysis.key_points[:2])}")

        return PromptSection(
            title="用户当前状态",
            content=content,
            priority=8,
            is_required=True
        )

    def _build_response_strategy(self, expression: EmotionExpression) -> PromptSection:
        """构建回复策略章节"""
        structure = expression.response_structure

        content = [
            f"**策略**: {structure['pattern']}",
            f"**长度**: {structure['length_guidance']}",
            f"**流程**: {' → '.join(structure['flow'])}"
        ]

        # 添加个性化建议
        personalization = structure['personalization']
        if personalization['techniques']:
            content.append(f"**技巧**: {', '.join(personalization['techniques'][:2])}")

        # 添加开场和结尾建议
        if expression.opening_suggestions and expression.opening_suggestions[0]:
            content.append(f"**开场参考**: {expression.opening_suggestions[0]}")

        return PromptSection(
            title="回复策略",
            content=content,
            priority=8,
            is_required=True
        )

    def _build_boundaries_section(self, expression: EmotionExpression) -> PromptSection:
        """构建边界和约束章节"""
        constraints = expression.intimacy_constraints

        content = []

        # 边界
        if constraints['boundaries']:
            content.append(f"**边界**: {', '.join(constraints['boundaries'][:2])}")

        # 禁止行为（如果有）
        if constraints['forbidden_behaviors']:
            content.append(f"**禁止**: {', '.join(constraints['forbidden_behaviors'][:2])}")

        # 不适当性警告
        if not expression.is_appropriate:
            content.insert(0, f"⚠️ **警告**: {constraints['violation_reason']}")

        # 适配注意事项
        if expression.adaptation_notes:
            for note in expression.adaptation_notes[:2]:
                content.append(note)

        return PromptSection(
            title="边界与约束",
            content=content,
            priority=7,
            is_required=True
        )

    def _build_special_instructions(self, instructions: str) -> PromptSection:
        """构建特殊指示章节"""
        return PromptSection(
            title="特殊指示",
            content=[instructions],
            priority=9,
            is_required=False
        )

    def _build_behavioral_goals(
        self,
        expression: EmotionExpression,
        level: str
    ) -> PromptSection:
        """构建行为目标章节"""
        level_config = get_level_config(level)

        content = [
            f"请以 {level_config.name} 关系的{expression.emotion_type}情感，真诚回复用户。",
            "保持自然、一致，体现对用户的了解和记忆。"
        ]

        # 根据情感类别添加特定目标
        if expression.emotion_category == "romantic":
            content.append("适度表达情感，保持浪漫氛围。")
        elif expression.emotion_category == "negative":
            content.append("提供理解和支持，帮助用户缓解负面情绪。")
        elif expression.emotion_category == "positive":
            content.append("分享喜悦，增进彼此感情。")

        return PromptSection(
            title="你的任务",
            content=content,
            priority=6,
            is_required=True
        )

    def _format_key(self, key: str) -> str:
        """格式化键名"""
        key_map = {
            "name": "姓名",
            "nickname": "昵称",
            "occupation": "职业",
            "interests": "兴趣",
            "preferences": "偏好",
            "age": "年龄",
            "location": "地区",
            "personality": "性格",
            "goals": "目标"
        }
        return key_map.get(key, key)

    def _assemble_prompt(self, sections: List[PromptSection], max_tokens: int) -> str:
        """
        组装提示词

        策略：
        1. 优先级排序
        2. 必需章节优先
        3. Token预算管理
        """
        # 分离必需和可选章节
        required_sections = [s for s in sections if s.is_required]
        optional_sections = [s for s in sections if not s.is_required]

        # 按优先级排序
        required_sections.sort(key=lambda x: x.priority, reverse=True)
        optional_sections.sort(key=lambda x: x.priority, reverse=True)

        # 构建提示词
        parts = []
        current_length = 0

        # 1. 添加所有必需章节
        for section in required_sections:
            section_text = self._format_section(section)
            parts.append(section_text)
            current_length += len(section_text)

        # 2. 添加可选章节（在预算内）
        for section in optional_sections:
            section_text = self._format_section(section)
            if current_length + len(section_text) <= max_tokens:
                parts.append(section_text)
                current_length += len(section_text)
            else:
                self.logger.warning(
                    f"[PromptBuilder] 跳过章节 '{section.title}' (预算不足)"
                )
                break

        return "\n\n".join(parts)

    def _format_section(self, section: PromptSection) -> str:
        """格式化章节"""
        lines = [f"# {section.title}"]
        lines.extend(section.content)
        return "\n".join(lines)


# 全局实例
dynamic_prompt_builder = DynamicPromptBuilder(max_tokens=2000)
