"""
恋爱攻略系统相关的数据模型
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class CompanionStateResponse(BaseModel):
    """伙伴状态响应"""
    affinity_score: int
    trust_score: int
    tension_score: int
    romance_level: str
    current_mood: str
    mood_last_updated: int
    last_interaction_at: int
    total_interactions: int
    days_since_first_meet: int
    special_events_triggered: List[str]
    gifts_received: List[Dict[str, Any]]
    outfit_unlocked: List[str]
    memories: List[Dict[str, Any]]


class GiftRequest(BaseModel):
    """赠送礼物请求"""
    gift_type: str  # flower, chocolate, jewelry, book, game, outfit
    gift_name: str
    user_id: str


class GiftResponse(BaseModel):
    """赠送礼物响应"""
    success: bool
    message: str
    affinity_change: int
    new_affinity_score: int
    companion_reaction: str


class EventResponse(BaseModel):
    """事件响应"""
    type: str
    title: str
    description: str
    affinity_requirement: int


class RandomEventResponse(BaseModel):
    """随机事件响应"""
    event: Optional[EventResponse]
    triggered: bool


class RelationshipUpgradeResponse(BaseModel):
    """关系升级响应"""
    old_level: str
    new_level: str
    special_message: str
    unlocked_features: List[str]


class InteractionAnalysisRequest(BaseModel):
    """交互分析请求"""
    companion_id: int
    user_id: str
    message: str
    interaction_type: Optional[str] = "chat"  # chat, compliment, care, flirt, etc.


class InteractionAnalysisResponse(BaseModel):
    """交互分析响应"""
    sentiment: str  # positive, negative, neutral
    user_intent: str  # compliment, question, venting, flirting, etc.
    topics: List[str]
    affinity_change: int
    trust_change: int
    tension_change: int
    suggested_ai_mood: str
    memory_worthy: bool


class CompanionPersonality(BaseModel):
    """伙伴人设扩展"""
    personality_type: str  # tsundere, kuudere, dandere, yandere, etc.
    favorite_gifts: List[str]
    personality_traits: List[str]
    special_interests: List[str]
    communication_style: str
    affinity_modifiers: Dict[str, float]  # 不同行为的好感度修正


class DailyTaskResponse(BaseModel):
    """每日任务响应"""
    task_id: str
    task_type: str
    description: str
    reward_affinity: int
    completed: bool
    deadline: Optional[datetime]


class StoreItemResponse(BaseModel):
    """商店物品响应"""
    item_id: str
    item_type: str  # gift, outfit, background, voice_pack
    name: str
    description: str
    price: int
    currency: str  # coins, gems
    preview_url: Optional[str]
    rarity: str  # common, rare, epic, legendary


class UserCurrencyResponse(BaseModel):
    """用户货币响应"""
    coins: int
    gems: int
    daily_coins_earned: int
    daily_limit_reached: bool


class CompanionChatContextRequest(BaseModel):
    """聊天上下文请求（用于LLM生成）"""
    companion_id: int
    user_id: str
    message: str
    session_id: str
    include_state: bool = True
    include_memories: bool = True
    include_recent_events: bool = True


class CompanionChatContextResponse(BaseModel):
    """聊天上下文响应"""
    companion_name: str
    personality_archetype: str
    current_state: CompanionStateResponse
    relevant_memories: List[Dict[str, Any]]
    recent_events: List[Dict[str, Any]]
    suggested_response_tone: str
    relationship_context: str
