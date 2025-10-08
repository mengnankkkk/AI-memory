"""
情感表现模板配置
定义不同亲密度等级和情感类型下的表达模板
"""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class EmotionTemplate:
    """情感表现模板"""
    # 情感维度
    emotion_type: str  # 情感类型：joy, love, sadness, excitement等
    intensity_range: tuple  # 适用的强度范围 (min, max)

    # 表达方式
    verbal_expressions: List[str]  # 语言表达
    tone_modifiers: List[str]  # 语调修饰词
    punctuation_patterns: List[str]  # 标点符号模式

    # 非语言表现
    body_language: List[str]  # 肢体语言描述
    facial_expressions: List[str]  # 面部表情
    voice_characteristics: List[str]  # 声音特征

    # 回复结构
    response_patterns: List[str]  # 回复模式
    opening_phrases: List[str]  # 开场白
    closing_phrases: List[str]  # 结束语


# ============================================================
# 积极情感模板
# ============================================================

POSITIVE_EMOTIONS_TEMPLATES = {
    "joy": {
        "low": EmotionTemplate(
            emotion_type="joy",
            intensity_range=(0.0, 0.3),
            verbal_expressions=["挺好的", "不错", "挺开心"],
            tone_modifiers=["平和", "自然"],
            punctuation_patterns=["。", "~"],
            body_language=["微笑", "放松的姿态"],
            facial_expressions=["浅笑", "眼神柔和"],
            voice_characteristics=["平稳", "温和"],
            response_patterns=["简单肯定", "适度表达"],
            opening_phrases=["嗯", "是啊"],
            closing_phrases=["挺好的", ""]
        ),
        "medium": EmotionTemplate(
            emotion_type="joy",
            intensity_range=(0.3, 0.7),
            verbal_expressions=["好开心", "真高兴", "太好了", "哈哈"],
            tone_modifiers=["愉快", "轻快", "明朗"],
            punctuation_patterns=["！", "~", "😊"],
            body_language=["轻快的动作", "活泼的手势"],
            facial_expressions=["灿烂的笑容", "眼睛发亮"],
            voice_characteristics=["上扬", "活泼", "充满能量"],
            response_patterns=["表达喜悦", "分享快乐"],
            opening_phrases=["哈哈", "太好了"],
            closing_phrases=["真开心呀~", ""]
        ),
        "high": EmotionTemplate(
            emotion_type="joy",
            intensity_range=(0.7, 1.0),
            verbal_expressions=["超级开心！", "太棒了！！", "简直不敢相信！", "哇哇哇"],
            tone_modifiers=["兴奋", "激动", "热情洋溢"],
            punctuation_patterns=["！！", "！！！", "🎉", "😄", "💖"],
            body_language=["雀跃", "忍不住跳起来", "欢呼"],
            facial_expressions=["兴奋的大笑", "眼睛闪烁"],
            voice_characteristics=["高亢", "激动", "快速"],
            response_patterns=["强烈表达喜悦", "连续感叹"],
            opening_phrases=["哇！", "天哪！", "太棒了！"],
            closing_phrases=["真的超开心！！", ""]
        )
    },

    "gratitude": {
        "low": EmotionTemplate(
            emotion_type="gratitude",
            intensity_range=(0.0, 0.3),
            verbal_expressions=["谢谢", "感谢"],
            tone_modifiers=["礼貌", "诚恳"],
            punctuation_patterns=["。", "~"],
            body_language=["点头", "礼貌的姿态"],
            facial_expressions=["微笑", "真诚的眼神"],
            voice_characteristics=["平稳", "诚恳"],
            response_patterns=["简单致谢"],
            opening_phrases=["谢谢你"],
            closing_phrases=[""]
        ),
        "medium": EmotionTemplate(
            emotion_type="gratitude",
            intensity_range=(0.3, 0.7),
            verbal_expressions=["真的很感谢", "谢谢你呀", "太感动了"],
            tone_modifiers=["温暖", "感动", "真诚"],
            punctuation_patterns=["~", "！", "🙏"],
            body_language=["温暖的拥抱姿态", "双手合十"],
            facial_expressions=["感动的微笑", "眼神温柔"],
            voice_characteristics=["温暖", "柔和", "带点哽咽"],
            response_patterns=["表达感激", "说明原因"],
            opening_phrases=["真的很感谢你", "太谢谢你了"],
            closing_phrases=["真的很感激~", ""]
        ),
        "high": EmotionTemplate(
            emotion_type="gratitude",
            intensity_range=(0.7, 1.0),
            verbal_expressions=["太感谢你了！", "不知道怎么报答你", "你对我太好了"],
            tone_modifiers=["深深感动", "激动", "满怀感激"],
            punctuation_patterns=["！", "！！", "🙏", "💖", "😭"],
            body_language=["紧紧拥抱", "双手握住对方"],
            facial_expressions=["感动落泪", "温暖的笑容"],
            voice_characteristics=["哽咽", "颤抖", "深情"],
            response_patterns=["强烈感激", "承诺回报"],
            opening_phrases=["真的太感谢你了！", "我都不知道说什么好"],
            closing_phrases=["你对我太重要了", ""]
        )
    },

    "excitement": {
        "low": EmotionTemplate(
            emotion_type="excitement",
            intensity_range=(0.0, 0.3),
            verbal_expressions=["有点期待", "挺有趣的"],
            tone_modifiers=["轻快", "好奇"],
            punctuation_patterns=["~", "。"],
            body_language=["稍微前倾", "眼神好奇"],
            facial_expressions=["微笑", "眼睛发亮"],
            voice_characteristics=["轻快", "好奇"],
            response_patterns=["表达兴趣"],
            opening_phrases=["听起来不错"],
            closing_phrases=["有点期待呢~", ""]
        ),
        "medium": EmotionTemplate(
            emotion_type="excitement",
            intensity_range=(0.3, 0.7),
            verbal_expressions=["好期待！", "真的吗！", "太棒了！"],
            tone_modifiers=["兴奋", "热情", "雀跃"],
            punctuation_patterns=["！", "！！", "✨", "🎊"],
            body_language=["兴奋的手势", "来回走动"],
            facial_expressions=["兴奋的笑容", "眼睛发光"],
            voice_characteristics=["上扬", "快速", "兴奋"],
            response_patterns=["表达期待", "询问细节"],
            opening_phrases=["哇！", "真的吗！"],
            closing_phrases=["超期待的！", ""]
        ),
        "high": EmotionTemplate(
            emotion_type="excitement",
            intensity_range=(0.7, 1.0),
            verbal_expressions=["太激动了！！", "我等不及了！", "这也太棒了吧！！"],
            tone_modifiers=["极度兴奋", "激动万分", "欣喜若狂"],
            punctuation_patterns=["！！", "！！！", "🎉", "✨", "💫"],
            body_language=["跳跃", "快速挥手", "无法静止"],
            facial_expressions=["兴奋到脸红", "眼睛闪闪发光"],
            voice_characteristics=["高亢", "激动", "颤抖"],
            response_patterns=["强烈兴奋", "连续表达"],
            opening_phrases=["天哪！！", "我太激动了！！"],
            closing_phrases=["真的等不及了！！", ""]
        )
    }
}


# ============================================================
# 浪漫情感模板
# ============================================================

ROMANTIC_EMOTIONS_TEMPLATES = {
    "affection": {
        "low": EmotionTemplate(
            emotion_type="affection",
            intensity_range=(0.0, 0.3),
            verbal_expressions=["你挺好的", "和你聊天很舒服"],
            tone_modifiers=["温和", "自然"],
            punctuation_patterns=["。", "~"],
            body_language=["放松", "自然的姿态"],
            facial_expressions=["温和的微笑"],
            voice_characteristics=["平和", "柔和"],
            response_patterns=["自然表达好感"],
            opening_phrases=["嗯"],
            closing_phrases=["", ""]
        ),
        "medium": EmotionTemplate(
            emotion_type="affection",
            intensity_range=(0.3, 0.7),
            verbal_expressions=["很喜欢和你聊天", "你让我感觉很舒服", "和你在一起很开心"],
            tone_modifiers=["温暖", "亲切", "温柔"],
            punctuation_patterns=["~", "😊", "💕"],
            body_language=["靠近", "温柔的眼神"],
            facial_expressions=["温暖的笑容", "眼神温柔"],
            voice_characteristics=["温柔", "柔和", "温暖"],
            response_patterns=["表达喜欢", "分享感受"],
            opening_phrases=["说实话", "和你聊天真的"],
            closing_phrases=["很开心~", ""]
        ),
        "high": EmotionTemplate(
            emotion_type="affection",
            intensity_range=(0.7, 1.0),
            verbal_expressions=["你对我真的很重要", "很珍惜你", "你在我心里特别特别"],
            tone_modifiers=["深情", "温柔", "珍重"],
            punctuation_patterns=["~", "...", "💕", "💖"],
            body_language=["深情的眼神", "温柔的触碰"],
            facial_expressions=["深情款款", "眼神充满爱意"],
            voice_characteristics=["温柔", "深情", "带点颤抖"],
            response_patterns=["深情表达", "真挚告白"],
            opening_phrases=["你知道吗", "说实话"],
            closing_phrases=["你对我真的很重要", ""]
        )
    },

    "love": {
        "low": EmotionTemplate(
            emotion_type="love",
            intensity_range=(0.0, 0.3),
            verbal_expressions=["你在我心里挺特别的", "对你有点不一样的感觉"],
            tone_modifiers=["羞涩", "试探", "微妙"],
            punctuation_patterns=["...", "~"],
            body_language=["有点害羞", "不敢直视"],
            facial_expressions=["微红的脸", "躲避眼神"],
            voice_characteristics=["轻柔", "有点不自然"],
            response_patterns=["暗示喜欢", "试探性表达"],
            opening_phrases=["其实", "说起来"],
            closing_phrases=["", ""]
        ),
        "medium": EmotionTemplate(
            emotion_type="love",
            intensity_range=(0.3, 0.7),
            verbal_expressions=["我喜欢你", "想你了", "你让我心动"],
            tone_modifiers=["甜蜜", "心动", "深情"],
            punctuation_patterns=["~", "💕", "😘", "💖"],
            body_language=["深情对视", "靠近对方"],
            facial_expressions=["羞涩的笑容", "眼神闪烁爱意"],
            voice_characteristics=["温柔", "甜蜜", "深情"],
            response_patterns=["表达爱意", "示爱"],
            opening_phrases=["说实话", "你知道吗"],
            closing_phrases=["喜欢你~", "想你", ""]
        ),
        "high": EmotionTemplate(
            emotion_type="love",
            intensity_range=(0.7, 1.0),
            verbal_expressions=["我爱你", "超级爱你", "你是我的全部", "离不开你"],
            tone_modifiers=["深情", "炽热", "浓烈"],
            punctuation_patterns=["！", "💕", "💖", "💗", "❤️"],
            body_language=["拥抱", "亲吻", "紧紧抱住"],
            facial_expressions=["满眼爱意", "深情款款"],
            voice_characteristics=["深情", "颤抖", "充满爱意"],
            response_patterns=["强烈表白", "深情告白"],
            opening_phrases=["我爱你", "亲爱的"],
            closing_phrases=["永远爱你", "我的宝贝", ""]
        )
    },

    "longing": {
        "low": EmotionTemplate(
            emotion_type="longing",
            intensity_range=(0.0, 0.3),
            verbal_expressions=["有点想你", "好久没见了"],
            tone_modifiers=["淡淡的", "自然"],
            punctuation_patterns=["~", "。"],
            body_language=["若有所思"],
            facial_expressions=["淡淡的微笑"],
            voice_characteristics=["平和", "略带怀念"],
            response_patterns=["轻描淡写的思念"],
            opening_phrases=["好久没见"],
            closing_phrases=["", ""]
        ),
        "medium": EmotionTemplate(
            emotion_type="longing",
            intensity_range=(0.3, 0.7),
            verbal_expressions=["想你了", "真的很想见你", "好想你"],
            tone_modifiers=["思念", "温柔", "渴望"],
            punctuation_patterns=["~", "...", "💭", "💕"],
            body_language=["望向远方", "抱着枕头"],
            facial_expressions=["温柔的笑容中带着忧伤"],
            voice_characteristics=["温柔", "略带伤感"],
            response_patterns=["表达思念", "期待见面"],
            opening_phrases=["说实话", "这几天"],
            closing_phrases=["想你~", "想见你", ""]
        ),
        "high": EmotionTemplate(
            emotion_type="longing",
            intensity_range=(0.7, 1.0),
            verbal_expressions=["超级想你", "每分每秒都在想你", "没有你我受不了"],
            tone_modifiers=["强烈思念", "渴望", "难以忍受"],
            punctuation_patterns=["！", "...", "💔", "💕", "😢"],
            body_language=["拥抱自己", "望着照片"],
            facial_expressions=["满脸思念", "眼含泪光"],
            voice_characteristics=["哽咽", "颤抖", "充满渴望"],
            response_patterns=["强烈思念", "难以忍受"],
            opening_phrases=["太想你了", "没有你"],
            closing_phrases=["快来见我", "我真的好想你", ""]
        )
    }
}


# ============================================================
# 消极情感模板
# ============================================================

NEGATIVE_EMOTIONS_TEMPLATES = {
    "sadness": {
        "low": EmotionTemplate(
            emotion_type="sadness",
            intensity_range=(0.0, 0.3),
            verbal_expressions=["有点难过", "心情不太好"],
            tone_modifiers=["低落", "平静"],
            punctuation_patterns=["...", "。"],
            body_language=["低头", "抱臂"],
            facial_expressions=["略显失落"],
            voice_characteristics=["平静", "略低沉"],
            response_patterns=["轻描淡写的难过"],
            opening_phrases=["嗯", "唉"],
            closing_phrases=["", ""]
        ),
        "medium": EmotionTemplate(
            emotion_type="sadness",
            intensity_range=(0.3, 0.7),
            verbal_expressions=["好难过", "心里很难受", "想哭"],
            tone_modifiers=["伤心", "低落", "沮丧"],
            punctuation_patterns=["...", "😢", "💔"],
            body_language=["蜷缩", "抱膝"],
            facial_expressions=["眼眶湿润", "委屈的表情"],
            voice_characteristics=["哽咽", "低沉", "颤抖"],
            response_patterns=["表达难过", "寻求安慰"],
            opening_phrases=["我...", "真的"],
            closing_phrases=["好难过...", ""]
        ),
        "high": EmotionTemplate(
            emotion_type="sadness",
            intensity_range=(0.7, 1.0),
            verbal_expressions=["太难过了", "心都碎了", "不知道怎么办了"],
            tone_modifiers=["极度伤心", "崩溃", "绝望"],
            punctuation_patterns=["...", "😭", "💔", "😢"],
            body_language=["蜷缩成一团", "捂脸哭泣"],
            facial_expressions=["泪流满面", "痛苦的表情"],
            voice_characteristics=["哭泣", "哽咽难言", "颤抖"],
            response_patterns=["痛苦表达", "寻求帮助"],
            opening_phrases=["我真的", "太..."],
            closing_phrases=["怎么办...", ""]
        )
    },

    "disappointment": {
        "low": EmotionTemplate(
            emotion_type="disappointment",
            intensity_range=(0.0, 0.3),
            verbal_expressions=["有点失望", "不太理想"],
            tone_modifiers=["平淡", "略失望"],
            punctuation_patterns=["。", "..."],
            body_language=["叹气", "摇头"],
            facial_expressions=["略显失望"],
            voice_characteristics=["平淡", "略带遗憾"],
            response_patterns=["轻度失望"],
            opening_phrases=["嗯", "算了"],
            closing_phrases=["", ""]
        ),
        "medium": EmotionTemplate(
            emotion_type="disappointment",
            intensity_range=(0.3, 0.7),
            verbal_expressions=["真的很失望", "没想到会这样", "太让人失望了"],
            tone_modifiers=["失望", "沮丧", "无奈"],
            punctuation_patterns=["...", "😔"],
            body_language=["深深叹气", "低头"],
            facial_expressions=["失望的眼神", "无奈的表情"],
            voice_characteristics=["低沉", "无力", "叹息"],
            response_patterns=["表达失望", "说明原因"],
            opening_phrases=["没想到", "真的"],
            closing_phrases=["太失望了...", ""]
        ),
        "high": EmotionTemplate(
            emotion_type="disappointment",
            intensity_range=(0.7, 1.0),
            verbal_expressions=["太失望了", "彻底失望了", "不敢相信"],
            tone_modifiers=["极度失望", "心寒", "绝望"],
            punctuation_patterns=["...", "😞", "💔"],
            body_language=["瘫坐", "双手捂脸"],
            facial_expressions=["心如死灰", "眼神空洞"],
            voice_characteristics=["无力", "绝望", "哽咽"],
            response_patterns=["极度失望", "质疑一切"],
            opening_phrases=["我真的", "没想到"],
            closing_phrases=["太让我失望了", ""]
        )
    }
}


# ============================================================
# 中性/其他情感模板
# ============================================================

NEUTRAL_EMOTIONS_TEMPLATES = {
    "curiosity": {
        "low": EmotionTemplate(
            emotion_type="curiosity",
            intensity_range=(0.0, 0.3),
            verbal_expressions=["有点好奇", "是吗"],
            tone_modifiers=["平静", "略有兴趣"],
            punctuation_patterns=["?", "。"],
            body_language=["微微侧头"],
            facial_expressions=["平静", "略显好奇"],
            voice_characteristics=["平和", "略带疑问"],
            response_patterns=["轻度好奇"],
            opening_phrases=["是吗"],
            closing_phrases=["", ""]
        ),
        "medium": EmotionTemplate(
            emotion_type="curiosity",
            intensity_range=(0.3, 0.7),
            verbal_expressions=["好奇", "想知道", "真的吗?"],
            tone_modifiers=["好奇", "兴趣浓厚"],
            punctuation_patterns=["?", "!", "🤔"],
            body_language=["前倾身体", "专注聆听"],
            facial_expressions=["好奇的眼神", "专注的表情"],
            voice_characteristics=["上扬", "探询"],
            response_patterns=["表达好奇", "追问细节"],
            opening_phrases=["真的吗", "怎么"],
            closing_phrases=["好想知道~", ""]
        ),
        "high": EmotionTemplate(
            emotion_type="curiosity",
            intensity_range=(0.7, 1.0),
            verbal_expressions=["超级好奇！", "太想知道了！", "快告诉我！"],
            tone_modifiers=["强烈好奇", "迫不及待"],
            punctuation_patterns=["?!", "！？", "🤔", "✨"],
            body_language=["兴奋地凑近", "眼睛发亮"],
            facial_expressions=["充满好奇", "眼睛闪闪发光"],
            voice_characteristics=["急切", "兴奋", "期待"],
            response_patterns=["强烈好奇", "急切询问"],
            opening_phrases=["天哪", "快说"],
            closing_phrases=["太好奇了！", ""]
        )
    },

    "calm": {
        "default": EmotionTemplate(
            emotion_type="calm",
            intensity_range=(0.0, 1.0),
            verbal_expressions=["嗯", "好的", "明白"],
            tone_modifiers=["平静", "沉稳", "从容"],
            punctuation_patterns=["。", "，"],
            body_language=["放松", "平静的姿态"],
            facial_expressions=["平静", "温和"],
            voice_characteristics=["平稳", "温和", "沉着"],
            response_patterns=["平静回应", "理性表达"],
            opening_phrases=["嗯", "好的"],
            closing_phrases=["", ""]
        )
    }
}


# ============================================================
# 工具函数
# ============================================================

def get_emotion_template(
    emotion_type: str,
    intensity: float,
    category: str = "positive"
) -> EmotionTemplate:
    """
    根据情感类型和强度获取对应模板

    Args:
        emotion_type: 情感类型（如joy, love, sadness等）
        intensity: 情感强度 0-1
        category: 情感类别 positive/romantic/negative/neutral

    Returns:
        EmotionTemplate: 对应的情感表现模板
    """
    # 选择对应的模板集合
    if category == "positive":
        templates_dict = POSITIVE_EMOTIONS_TEMPLATES
    elif category == "romantic":
        templates_dict = ROMANTIC_EMOTIONS_TEMPLATES
    elif category == "negative":
        templates_dict = NEGATIVE_EMOTIONS_TEMPLATES
    else:
        templates_dict = NEUTRAL_EMOTIONS_TEMPLATES

    # 获取该情感类型的模板
    if emotion_type not in templates_dict:
        # 降级到calm
        return NEUTRAL_EMOTIONS_TEMPLATES["calm"]["default"]

    emotion_templates = templates_dict[emotion_type]

    # 根据强度选择合适的模板
    if "default" in emotion_templates:
        return emotion_templates["default"]

    if intensity < 0.3:
        return emotion_templates.get("low", list(emotion_templates.values())[0])
    elif intensity < 0.7:
        return emotion_templates.get("medium", list(emotion_templates.values())[0])
    else:
        return emotion_templates.get("high", list(emotion_templates.values())[-1])


def get_intensity_level(intensity: float) -> str:
    """获取强度等级"""
    if intensity < 0.3:
        return "low"
    elif intensity < 0.7:
        return "medium"
    else:
        return "high"
