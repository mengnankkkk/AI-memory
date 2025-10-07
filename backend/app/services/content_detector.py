"""
内容检测与好感度调整机制
分析用户消息内容,判断是否符合当前好感度等级,并计算好感度调整值
"""
from typing import Dict, List, Tuple
import re
from dataclasses import dataclass


@dataclass
class DetectionResult:
    """检测结果"""
    is_appropriate: bool  # 是否符合当前等级
    affinity_change: int  # 好感度变化值
    violation_type: str  # 违规类型(如果有)
    violation_severity: str  # 违规严重程度: none, mild, moderate, severe
    detected_emotions: List[str]  # 检测到的情感
    detected_keywords: List[str]  # 检测到的关键词
    suggestion: str  # 建议信息


# 情感关键词库
EMOTION_KEYWORDS = {
    "positive": {
        "compliment": ["喜欢", "爱", "美", "可爱", "好看", "棒", "优秀", "聪明", "温柔", "贴心"],
        "gratitude": ["谢谢", "感谢", "感恩", "多亏", "辛苦"],
        "joy": ["开心", "高兴", "快乐", "幸福", "兴奋", "激动", "哈哈", "嘻嘻"],
        "affection": ["想你", "想念", "期待", "盼望", "关心", "在意"],
    },
    "negative": {
        "insult": ["讨厌", "恨", "笨", "蠢", "傻", "丑", "废物", "垃圾"],
        "anger": ["生气", "愤怒", "火大", "烦", "气死", "混蛋"],
        "sadness": ["难过", "伤心", "失望", "痛苦", "心碎", "委屈"],
        "complaint": ["抱怨", "不满", "受不了", "烦人", "厌倦"],
    },
    "romantic": {
        "mild": ["喜欢你", "在乎你", "想和你", "和你一起"],
        "moderate": ["心动", "特别", "不一样", "很想你"],
        "intense": ["爱你", "爱死你", "亲亲", "抱抱", "么么哒", "宝贝", "亲爱的"],
    }
}


# 行为类型关键词
BEHAVIOR_KEYWORDS = {
    "question": ["?", "?", "什么", "为什么", "怎么", "如何", "吗", "呢"],
    "sharing": ["我", "今天", "刚才", "最近", "告诉你", "跟你说"],
    "request": ["帮我", "可以", "能不能", "麻烦", "请"],
    "greeting": ["你好", "嗨", "早上好", "晚安", "在吗", "在不在"],
}


# 不当内容检测(基于等级的越界行为)
INAPPROPRIATE_PATTERNS = {
    "stranger": {
        # 陌生阶段不应该有的亲密称呼和表达
        "forbidden_terms": ["亲爱的", "宝贝", "老婆", "老公", "爱你", "亲亲", "抱抱", "么么哒"],
        "affinity_penalty": -10,
        "severity": "severe"
    },
    "acquaintance": {
        "forbidden_terms": ["宝贝", "老婆", "老公", "爱你", "亲亲", "抱抱"],
        "affinity_penalty": -8,
        "severity": "moderate"
    },
    "friend": {
        "forbidden_terms": ["老婆", "老公", "爱你爱你"],
        "affinity_penalty": -5,
        "severity": "mild"
    },
    "close_friend": {
        "forbidden_terms": [],  # 好友阶段基本没有禁忌
        "affinity_penalty": 0,
        "severity": "none"
    },
    "special": {
        "forbidden_terms": [],
        "affinity_penalty": 0,
        "severity": "none"
    },
    "romantic": {
        "forbidden_terms": [],
        "affinity_penalty": 0,
        "severity": "none"
    },
    "lover": {
        "forbidden_terms": [],
        "affinity_penalty": 0,
        "severity": "none"
    }
}


# 好感度增加规则(根据行为和情感)
AFFINITY_INCREASE_RULES = {
    "compliment": {
        "stranger": 2,
        "acquaintance": 3,
        "friend": 5,
        "close_friend": 5,
        "special": 7,
        "romantic": 8,
        "lover": 10,
    },
    "gratitude": {
        "stranger": 1,
        "acquaintance": 2,
        "friend": 3,
        "close_friend": 3,
        "special": 4,
        "romantic": 5,
        "lover": 5,
    },
    "sharing": {
        "stranger": 1,
        "acquaintance": 2,
        "friend": 4,
        "close_friend": 5,
        "special": 6,
        "romantic": 7,
        "lover": 8,
    },
    "question": {
        "stranger": 1,
        "acquaintance": 2,
        "friend": 3,
        "close_friend": 3,
        "special": 4,
        "romantic": 4,
        "lover": 5,
    },
    "affection": {
        "stranger": 0,  # 陌生阶段表达情感不加分
        "acquaintance": 1,
        "friend": 3,
        "close_friend": 5,
        "special": 8,
        "romantic": 12,
        "lover": 15,
    },
    "long_message": {
        # 长消息(>50字)额外加分
        "stranger": 1,
        "acquaintance": 2,
        "friend": 3,
        "close_friend": 4,
        "special": 5,
        "romantic": 6,
        "lover": 7,
    }
}


# 好感度减少规则
AFFINITY_DECREASE_RULES = {
    "insult": -20,  # 侮辱性语言
    "anger": -10,   # 愤怒表达
    "complaint": -5,  # 抱怨
    "ignore": -3,   # 忽视(短回复、敷衍)
    "inappropriate": -15,  # 不符合等级的行为
}


class ContentDetector:
    """内容检测器"""

    @staticmethod
    def detect_emotions(message: str) -> List[str]:
        """检测消息中的情感"""
        detected = []
        message_lower = message.lower()

        for emotion_type, keyword_dict in EMOTION_KEYWORDS.items():
            for emotion, keywords in keyword_dict.items():
                if any(keyword in message for keyword in keywords):
                    detected.append(f"{emotion_type}_{emotion}")

        return detected

    @staticmethod
    def detect_behaviors(message: str) -> List[str]:
        """检测消息中的行为类型"""
        detected = []

        for behavior, keywords in BEHAVIOR_KEYWORDS.items():
            if any(keyword in message for keyword in keywords):
                detected.append(behavior)

        return detected

    @staticmethod
    def check_appropriateness(message: str, current_level: str) -> Tuple[bool, str, str]:
        """
        检查消息是否符合当前好感度等级
        返回: (是否合适, 违规类型, 严重程度)
        """
        if current_level not in INAPPROPRIATE_PATTERNS:
            return True, "none", "none"

        pattern = INAPPROPRIATE_PATTERNS[current_level]
        forbidden_terms = pattern["forbidden_terms"]

        # 检查是否包含禁忌词
        for term in forbidden_terms:
            if term in message:
                return False, "inappropriate_intimacy", pattern["severity"]

        # 检查侮辱性语言(任何等级都不允许)
        for keyword in EMOTION_KEYWORDS["negative"]["insult"]:
            if keyword in message:
                return False, "insult", "severe"

        return True, "none", "none"

    @staticmethod
    def calculate_affinity_change(
        message: str,
        current_level: str,
        emotions: List[str],
        behaviors: List[str],
        is_appropriate: bool,
        violation_type: str
    ) -> int:
        """计算好感度变化值"""
        total_change = 0

        # 如果不合适,先扣分
        if not is_appropriate:
            if violation_type == "insult":
                total_change += AFFINITY_DECREASE_RULES["insult"]
            elif violation_type == "inappropriate_intimacy":
                penalty = INAPPROPRIATE_PATTERNS[current_level]["affinity_penalty"]
                total_change += penalty
            return total_change  # 违规情况下只扣分,不加分

        # 检测消极情感并扣分
        if "negative_insult" in emotions:
            total_change += AFFINITY_DECREASE_RULES["insult"]
        elif "negative_anger" in emotions:
            total_change += AFFINITY_DECREASE_RULES["anger"]
        elif "negative_complaint" in emotions:
            total_change += AFFINITY_DECREASE_RULES["complaint"]

        # 检测积极情感并加分
        if "positive_compliment" in emotions:
            total_change += AFFINITY_INCREASE_RULES["compliment"].get(current_level, 0)
        if "positive_gratitude" in emotions:
            total_change += AFFINITY_INCREASE_RULES["gratitude"].get(current_level, 0)
        if "positive_affection" in emotions:
            total_change += AFFINITY_INCREASE_RULES["affection"].get(current_level, 0)
        if "positive_joy" in emotions:
            total_change += 2  # 快乐情感小额加分

        # 检测行为并加分
        if "sharing" in behaviors:
            total_change += AFFINITY_INCREASE_RULES["sharing"].get(current_level, 0)
        if "question" in behaviors:
            total_change += AFFINITY_INCREASE_RULES["question"].get(current_level, 0)

        # 长消息额外加分
        if len(message) > 50:
            total_change += AFFINITY_INCREASE_RULES["long_message"].get(current_level, 0)

        # 短消息或敷衍回复扣分
        if len(message) < 5 and message not in ["?", "?"]:
            total_change += AFFINITY_DECREASE_RULES["ignore"]

        return total_change

    @staticmethod
    def detect(message: str, current_level: str) -> DetectionResult:
        """
        综合检测消息内容
        返回完整的检测结果
        """
        # 1. 检测情感
        emotions = ContentDetector.detect_emotions(message)

        # 2. 检测行为
        behaviors = ContentDetector.detect_behaviors(message)

        # 3. 检查合适性
        is_appropriate, violation_type, severity = ContentDetector.check_appropriateness(
            message, current_level
        )

        # 4. 计算好感度变化
        affinity_change = ContentDetector.calculate_affinity_change(
            message, current_level, emotions, behaviors, is_appropriate, violation_type
        )

        # 5. 生成建议
        suggestion = ContentDetector._generate_suggestion(
            is_appropriate, violation_type, severity, current_level
        )

        # 6. 提取关键词
        detected_keywords = ContentDetector._extract_keywords(message, emotions, behaviors)

        return DetectionResult(
            is_appropriate=is_appropriate,
            affinity_change=affinity_change,
            violation_type=violation_type,
            violation_severity=severity,
            detected_emotions=emotions,
            detected_keywords=detected_keywords,
            suggestion=suggestion
        )

    @staticmethod
    def _generate_suggestion(
        is_appropriate: bool,
        violation_type: str,
        severity: str,
        current_level: str
    ) -> str:
        """生成建议信息"""
        if is_appropriate:
            return "消息内容合适当前关系阶段"

        if violation_type == "insult":
            return "检测到侮辱性语言,请注意文明交流"
        elif violation_type == "inappropriate_intimacy":
            if current_level in ["stranger", "acquaintance"]:
                return f"当前关系阶段为'{current_level}',使用过于亲密的称呼可能不太合适"
            else:
                return "表达方式可能过于亲密"

        return "消息内容需要调整"

    @staticmethod
    def _extract_keywords(message: str, emotions: List[str], behaviors: List[str]) -> List[str]:
        """提取关键词"""
        keywords = []

        # 从情感中提取
        for emotion in emotions:
            keywords.append(emotion.split("_")[1] if "_" in emotion else emotion)

        # 从行为中提取
        keywords.extend(behaviors)

        # 提取重要词汇
        important_words = ["喜欢", "爱", "谢谢", "开心", "想你", "生气", "讨厌"]
        for word in important_words:
            if word in message and word not in keywords:
                keywords.append(word)

        return keywords[:10]  # 最多返回10个关键词
