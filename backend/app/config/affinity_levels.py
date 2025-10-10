"""
好感度分级配置系统
定义好感度等级、数值范围、行为特征等核心配置
"""
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class AffinityLevel:
    """好感度等级配置"""
    name: str  # 等级名称
    min_score: int  # 最小分数
    max_score: int  # 最大分数
    description: str  # 等级描述
    addressing_style: List[str]  # 称呼方式
    tone_keywords: List[str]  # 语气关键词
    emoji_usage: str  # 表情符号使用规则: none, minimal, moderate, frequent
    intimacy_level: int  # 亲密度 1-10
    response_formality: str  # 回复正式度: formal, semi-formal, casual, intimate


# 好感度等级定义 (7个等级,分数范围0-1000)
AFFINITY_LEVELS: Dict[str, AffinityLevel] = {
    "stranger": AffinityLevel(
        name="陌生",
        min_score=0,
        max_score=100,
        description="刚刚认识,保持基本礼貌和距离感",
        addressing_style=["您", "先生/女士", "对方"],
        tone_keywords=["请", "谢谢", "抱歉", "打扰"],
        emoji_usage="none",
        intimacy_level=1,
        response_formality="formal"
    ),
    "acquaintance": AffinityLevel(
        name="认识",
        min_score=101,
        max_score=250,
        description="有了初步了解,可以进行基本交流",
        addressing_style=["你", "朋友"],
        tone_keywords=["好的", "明白", "不错"],
        emoji_usage="minimal",
        intimacy_level=3,
        response_formality="semi-formal"
    ),
    "friend": AffinityLevel(
        name="朋友",
        min_score=251,
        max_score=450,
        description="建立了友谊,交流轻松自然",
        addressing_style=["你", "朋友", "小伙伴"],
        tone_keywords=["哈哈", "嗯嗯", "好呀", "挺好"],
        emoji_usage="moderate",
        intimacy_level=5,
        response_formality="casual"
    ),
    "close_friend": AffinityLevel(
        name="好友",
        min_score=451,
        max_score=600,
        description="深入了解,有较强的信任和默契",
        addressing_style=["你", "好友", "伙伴"],
        tone_keywords=["真的", "感动", "开心", "谢啦"],
        emoji_usage="moderate",
        intimacy_level=6,
        response_formality="casual"
    ),
    "special": AffinityLevel(
        name="特别的人",
        min_score=601,
        max_score=750,
        description="对方变得特别,开始有微妙的情感",
        addressing_style=["你", "昵称"],
        tone_keywords=["嘿嘿", "其实", "有点", "感觉"],
        emoji_usage="frequent",
        intimacy_level=7,
        response_formality="casual"
    ),
    "romantic": AffinityLevel(
        name="心动",
        min_score=751,
        max_score=900,
        description="心动的感觉,但还未正式确认关系",
        addressing_style=["你", "昵称", "小可爱"],
        tone_keywords=["嘻嘻", "想你", "期待", "开心"],
        emoji_usage="frequent",
        intimacy_level=8,
        response_formality="intimate"
    ),
    "lover": AffinityLevel(
        name="恋人",
        min_score=901,
        max_score=1000,
        description="确认恋爱关系,深厚感情",
        addressing_style=["亲爱的", "宝贝", "darling", "昵称"],
        tone_keywords=["爱你", "想你", "亲亲", "抱抱", "么么哒"],
        emoji_usage="frequent",
        intimacy_level=10,
        response_formality="intimate"
    )
}


# 好感度等级顺序(用于升级和降级判断)
LEVEL_ORDER = [
    "stranger", "acquaintance", "friend",
    "close_friend", "special", "romantic", "lover"
]


# 兼容别名映射（含中文显示名与同义词）
_LEVEL_ALIAS_MAP: Dict[str, str] = {
    **{key: key for key in AFFINITY_LEVELS.keys()},
    **{level.name: key for key, level in AFFINITY_LEVELS.items()}
}

# 额外的中文别名
_LEVEL_ALIAS_MAP.update({
    "初识": "stranger",
    "初识阶段": "stranger",
    "认识": "acquaintance",
    "普通朋友": "acquaintance",
    "好朋友": "friend",
    "好友": "close_friend",
    "特别的人": "special",
    "心动": "romantic",
    "恋人": "lover",
    "深爱": "lover"
})


def normalize_level_key(level: str) -> str:
    """将任意形式的等级标识转换为标准英文键名。"""

    if not level:
        return "stranger"

    candidate = level.strip()
    if not candidate:
        return "stranger"

    # 先尝试直接匹配（区分大小写）
    if candidate in _LEVEL_ALIAS_MAP:
        return _LEVEL_ALIAS_MAP[candidate]

    # 英文键名大小写不敏感处理
    lowered = candidate.lower()
    for key in AFFINITY_LEVELS.keys():
        if lowered == key.lower():
            return key

    # 处理包含空格/连字符的形式
    sanitized = lowered.replace(" ", "_").replace("-", "_")
    if sanitized in AFFINITY_LEVELS:
        return sanitized

    return "stranger"


def get_level_by_score(score: int) -> str:
    """根据分数获取等级名称"""
    # 确保分数在有效范围内
    score = max(0, min(1000, score))

    for level_key in LEVEL_ORDER:
        level = AFFINITY_LEVELS[level_key]
        if level.min_score <= score <= level.max_score:
            return level_key

    return "stranger"  # 默认返回陌生


def get_level_config(level_key: str) -> AffinityLevel:
    """获取等级配置"""
    normalized = normalize_level_key(level_key)
    return AFFINITY_LEVELS.get(normalized, AFFINITY_LEVELS["stranger"])


def get_next_level(current_level: str) -> str:
    """获取下一个等级"""
    try:
        index = LEVEL_ORDER.index(normalize_level_key(current_level))
        if index < len(LEVEL_ORDER) - 1:
            return LEVEL_ORDER[index + 1]
        return current_level  # 已是最高等级
    except ValueError:
        return "stranger"


def get_previous_level(current_level: str) -> str:
    """获取上一个等级"""
    try:
        index = LEVEL_ORDER.index(normalize_level_key(current_level))
        if index > 0:
            return LEVEL_ORDER[index - 1]
        return current_level  # 已是最低等级
    except ValueError:
        return "stranger"


# 好感度边界配置
AFFINITY_BOUNDARIES = {
    "absolute_min": 0,      # 绝对最小值
    "absolute_max": 1000,   # 绝对最大值
    "safe_min": 50,         # 安全最小值(低于此值会触发保护机制)
    "safe_max": 950,        # 安全最大值(高于此值会减缓增长)
    "warning_threshold": 100,  # 警告阈值(单次变化)
}


# 好感度调整速率配置(用于容错机制)
ADJUSTMENT_RATES = {
    "normal": 1.0,          # 正常速率
    "accelerated": 1.5,     # 加速(好感度低时)
    "decelerated": 0.5,     # 减速(好感度高时)
    "protected": 0.3,       # 保护模式(接近边界时)
}


# 单次调整限制(容错机制)
SINGLE_ADJUSTMENT_LIMITS = {
    "max_increase": 50,     # 单次最大增加
    "max_decrease": 30,     # 单次最大减少
    "critical_decrease": 20,  # 严重违规最大减少
}
