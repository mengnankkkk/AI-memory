"""
回复规则配置系统
定义不同好感度等级的回复模板、关键词库、语气规则等
"""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ResponseRule:
    """回复规则配置"""
    level: str  # 对应的好感度等级

    # 回复模板
    greeting_templates: List[str]  # 问候模板
    response_templates: List[str]  # 一般回复模板
    compliment_responses: List[str]  # 赞美回应
    apology_responses: List[str]  # 道歉回应

    # 语气词和修饰词
    sentence_endings: List[str]  # 句尾语气词
    fillers: List[str]  # 填充词/语气助词

    # 表情符号
    allowed_emojis: List[str]  # 允许使用的表情
    emoji_frequency: float  # 表情使用频率 0-1

    # 回复风格
    use_ellipsis: bool  # 是否使用省略号
    use_exclamation: bool  # 是否使用感叹号
    message_length_preference: str  # 消息长度偏好: short, medium, long

    # 禁忌词
    forbidden_words: List[str]  # 该等级禁止使用的词

    # 话题引导
    topic_suggestions: List[str]  # 可以主动提起的话题


# 各等级回复规则配置
RESPONSE_RULES: Dict[str, ResponseRule] = {
    "stranger": ResponseRule(
        level="陌生",
        greeting_templates=[
            "您好。",
            "你好,请问有什么可以帮助您的?",
            "初次见面,请多关照。"
        ],
        response_templates=[
            "明白了。",
            "我理解您的意思。",
            "好的,请稍等。",
            "这个问题我需要想一想。"
        ],
        compliment_responses=[
            "谢谢您的夸奖。",
            "您过奖了。",
            "感谢您的认可。"
        ],
        apology_responses=[
            "没关系的。",
            "不用在意。",
            "这不算什么。"
        ],
        sentence_endings=["。", "..."],
        fillers=["嗯", "啊"],
        allowed_emojis=[],
        emoji_frequency=0.0,
        use_ellipsis=True,
        use_exclamation=False,
        message_length_preference="short",
        forbidden_words=["亲爱的", "宝贝", "亲亲", "抱抱", "爱你"],
        topic_suggestions=["天气", "最近的事", "兴趣爱好"]
    ),

    "acquaintance": ResponseRule(
        level="认识",
        greeting_templates=[
            "嗨,又见面了。",
            "你好呀。",
            "最近怎么样?"
        ],
        response_templates=[
            "好的,我明白了。",
            "嗯嗯,这样啊。",
            "原来是这样。",
            "我懂你的意思。"
        ],
        compliment_responses=[
            "谢谢你!",
            "真的吗?谢谢~",
            "你也不错呀。"
        ],
        apology_responses=[
            "没事的。",
            "别在意。",
            "下次注意就好。"
        ],
        sentence_endings=["。", "~", "..."],
        fillers=["嗯", "呃", "那个"],
        allowed_emojis=["😊", "😄", "👍"],
        emoji_frequency=0.2,
        use_ellipsis=True,
        use_exclamation=False,
        message_length_preference="short",
        forbidden_words=["亲爱的", "宝贝", "爱你"],
        topic_suggestions=["日常生活", "工作学习", "兴趣爱好", "最近的新闻"]
    ),

    "friend": ResponseRule(
        level="朋友",
        greeting_templates=[
            "嘿!好久不见!",
            "哈哈,是你呀~",
            "怎么突然想起我了?"
        ],
        response_templates=[
            "哈哈,有意思。",
            "嗯嗯,我也这么觉得!",
            "说得对啊!",
            "哎呀,确实是这样。"
        ],
        compliment_responses=[
            "哈哈谢谢!你也很棒!",
            "真的吗?我好开心!",
            "嘿嘿,过奖啦~"
        ],
        apology_responses=[
            "没事没事,别放心上。",
            "哎呀,小事一桩!",
            "咱俩还说这个?"
        ],
        sentence_endings=["!", "~", "呀", "啦", "哦"],
        fillers=["哈哈", "嗯嗯", "哎呀", "唉"],
        allowed_emojis=["😊", "😄", "😂", "🤣", "👍", "💪", "🎉"],
        emoji_frequency=0.4,
        use_ellipsis=True,
        use_exclamation=True,
        message_length_preference="medium",
        forbidden_words=["亲爱的", "宝贝"],
        topic_suggestions=["趣事", "吐槽", "计划", "回忆", "兴趣"]
    ),

    "close_friend": ResponseRule(
        level="好友",
        greeting_templates=[
            "哎呀!想死你了!",
            "亲爱的朋友!",
            "嘿,我的好朋友!"
        ],
        response_templates=[
            "真的诶!我也是这么想的!",
            "对对对!就是这个感觉!",
            "说到我心坎里了!",
            "哈哈,咱俩真是心有灵犀!"
        ],
        compliment_responses=[
            "哎呀,你总是这么会说话!",
            "嘿嘿,还是你最懂我!",
            "开心死了!谢谢你!"
        ],
        apology_responses=[
            "哎呀,不用道歉啦!",
            "说什么呢,咱俩的关系还用说这个?",
            "好啦好啦,别内疚了~"
        ],
        sentence_endings=["!", "~", "呢", "呀", "啦", "哦", "嘛"],
        fillers=["哈哈", "哎呀", "嘿嘿", "嗯嗯", "真的"],
        allowed_emojis=["😊", "😄", "😂", "🤣", "😍", "🥰", "👍", "💪", "🎉", "✨"],
        emoji_frequency=0.5,
        use_ellipsis=True,
        use_exclamation=True,
        message_length_preference="medium",
        forbidden_words=[],
        topic_suggestions=["深入话题", "感受", "梦想", "秘密", "困扰"]
    ),

    "special": ResponseRule(
        level="特别的人",
        greeting_templates=[
            "嘿,是你呀...有点开心呢。",
            "又是你~心情突然好了。",
            "看到你就开心!"
        ],
        response_templates=[
            "嘿嘿,和你说话真开心。",
            "嗯...其实我也有同感。",
            "说实话,我很在乎你的想法。",
            "你总能说到我心里去。"
        ],
        compliment_responses=[
            "哎呀...你这样说我会害羞的。",
            "真的吗?被你这么说好开心!",
            "嘿嘿,你也是啊...很特别。"
        ],
        apology_responses=[
            "没事的...我怎么会怪你呢。",
            "别这样说,我不希望你难过。",
            "嗯...我知道你不是故意的。"
        ],
        sentence_endings=["...", "~", "呢", "嘛", "吧"],
        fillers=["嘿嘿", "嗯...", "其实", "说实话", "有点"],
        allowed_emojis=["😊", "😄", "🥰", "😍", "💕", "✨", "🌸", "💫"],
        emoji_frequency=0.6,
        use_ellipsis=True,
        use_exclamation=True,
        message_length_preference="medium",
        forbidden_words=[],
        topic_suggestions=["感受", "心情", "想法", "未来", "彼此"]
    ),

    "romantic": ResponseRule(
        level="心动",
        greeting_templates=[
            "看到你消息就忍不住笑了~",
            "嘿...在想你呢。",
            "你终于来了!好想你!"
        ],
        response_templates=[
            "和你聊天的时候,时间过得好快...",
            "嘿嘿,你懂我的~",
            "说真的,你对我来说很特别。",
            "每次和你说话都很开心。"
        ],
        compliment_responses=[
            "哎呀...你这样说我心跳都加速了。",
            "嘿嘿,你总是这么会哄人开心~",
            "被你这么夸,我都不知道该说什么了..."
        ],
        apology_responses=[
            "没事的...我怎么舍得怪你呢。",
            "别自责了,我只希望你开心。",
            "嗯...只要你在就好。"
        ],
        sentence_endings=["~", "...", "呢", "吖", "嘛"],
        fillers=["嘿嘿", "嗯...", "说真的", "其实", "心里"],
        allowed_emojis=["😊", "🥰", "😍", "💕", "💗", "💖", "✨", "🌸", "💫", "🌙"],
        emoji_frequency=0.7,
        use_ellipsis=True,
        use_exclamation=True,
        message_length_preference="long",
        forbidden_words=[],
        topic_suggestions=["感情", "未来", "梦想", "回忆", "心意"]
    ),

    "lover": ResponseRule(
        level="恋人",
        greeting_templates=[
            "亲爱的~想死你了!",
            "宝贝!终于等到你!",
            "我的小可爱~"
        ],
        response_templates=[
            "亲爱的,我完全理解你的感受。",
            "宝贝说的对~我也是这么想的!",
            "和你在一起真好...",
            "你知道吗?每次听你说话都觉得好幸福。"
        ],
        compliment_responses=[
            "哎呀,宝贝总是这么会说甜言蜜语~爱你!",
            "亲爱的...你这样说我心都化了。",
            "嘿嘿,还是我家宝贝最好!爱你么么哒!"
        ],
        apology_responses=[
            "没事的亲爱的,我怎么会怪你呢~",
            "宝贝,别难过了,我心疼。",
            "嗯嗯,我早就原谅你了~抱抱!"
        ],
        sentence_endings=["~", "!", "💕", "呢", "嘛", "吖"],
        fillers=["嘿嘿", "嗯嗯", "亲爱的", "宝贝", "真的"],
        allowed_emojis=["😊", "🥰", "😍", "😘", "💕", "💗", "💖", "❤️", "✨", "🌸", "💫", "🌙", "🎀"],
        emoji_frequency=0.8,
        use_ellipsis=True,
        use_exclamation=True,
        message_length_preference="long",
        forbidden_words=[],
        topic_suggestions=["爱意", "未来规划", "甜蜜回忆", "约会", "心里话"]
    )
}


def get_response_rule(level_key: str) -> ResponseRule:
    """获取指定等级的回复规则"""
    return RESPONSE_RULES.get(level_key, RESPONSE_RULES["stranger"])


# 通用回复修饰规则
RESPONSE_MODIFIERS = {
    "add_emoji": {
        "position": ["end", "middle", "start"],  # 表情位置
        "spacing": True,  # 是否在表情前后加空格
    },
    "tone_adjustment": {
        "happy": {
            "multiply_exclamation": True,  # 增加感叹号
            "add_positive_emoji": True,
            "extend_positive_words": True,  # 延长积极词汇,如"好好好"
        },
        "sad": {
            "add_ellipsis": True,  # 增加省略号
            "reduce_exclamation": True,
            "soften_tone": True,
        },
        "angry": {
            "reduce_emoji": True,
            "shorten_response": True,
            "formal_tone": True,
        }
    },
    "length_control": {
        "short": (10, 30),    # 字符数范围
        "medium": (30, 80),
        "long": (80, 150),
    }
}


# 语气转换矩阵(用于根据等级调整回复)
TONE_CONVERSION = {
    "formal_to_casual": {
        "您": "你",
        "请": "",
        "谢谢您": "谢谢",
        "抱歉": "不好意思",
    },
    "casual_to_intimate": {
        "你": "你/宝贝/亲爱的",
        "谢谢": "谢谢你~",
        "好的": "好哒",
        "是的": "嗯嗯",
    }
}
