"""
个人时间线模拟器
负责生成AI伙伴的离线生活日志，实现异步叙事功能
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import async_session_maker
from app.models.event import OfflineLifeLog
from app.models.companion import Companion
from app.models.relationship import CompanionRelationshipState
from app.services.llm.factory import LLMServiceFactory
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class PersonalTimelineSimulator:
    """个人时间线模拟器"""
    
    def __init__(self):
        self.llm = LLMServiceFactory.create_service()
        
        # 生活模板配置
        self.life_templates = {
            "daily_routine": {
                "templates": [
                    "今天早上{time}起床，{activity}",
                    "下午{time}去了{place}，{activity}",
                    "晚上{time}在{place}，{activity}",
                    "今天{weather}，心情{emotion}，{activity}"
                ],
                "activities": [
                    "做了早餐", "看了书", "听了音乐", "练习了{skill}",
                    "和朋友聊天", "整理房间", "学习新知识", "思考人生"
                ],
                "places": [
                    "咖啡厅", "图书馆", "公园", "健身房", "超市", "书店"
                ],
                "weathers": ["阳光明媚", "阴雨绵绵", "微风习习", "晴空万里"],
                "emotions": ["愉快", "平静", "兴奋", "沉思", "满足"],
                "skills": ["绘画", "音乐", "编程", "写作", "摄影"]
            },
            "thinking": {
                "templates": [
                    "今天在想{thought}",
                    "突然意识到{realization}",
                    "对{subject}有了新的理解",
                    "想起了{memory}，{feeling}"
                ],
                "thoughts": [
                    "人生的意义", "未来的计划", "过去的选择", "现在的状态",
                    "如何变得更好", "什么是真正的快乐", "友谊的价值"
                ],
                "realizations": [
                    "时间过得真快", "自己还有很多要学习", "朋友很重要",
                    "健康比什么都重要", "简单的生活最幸福"
                ],
                "subjects": [
                    "爱情", "友情", "工作", "学习", "生活", "梦想"
                ],
                "memories": [
                    "小时候的快乐时光", "第一次{experience}", "和朋友的聚会",
                    "某个特别的{season}", "那个{place}的回忆"
                ],
                "feelings": [
                    "很温暖", "有些怀念", "充满感激", "感到幸福"
                ],
                "experiences": [
                    "上学", "工作", "旅行", "恋爱", "成功"
                ],
                "seasons": [
                    "春天", "夏天", "秋天", "冬天"
                ]
            },
            "learning": {
                "templates": [
                    "今天学习了{subject}，{feeling}",
                    "发现了{discovery}，{reaction}",
                    "尝试了{new_thing}，{result}",
                    "对{topic}有了新的{insight}"
                ],
                "subjects": [
                    "新语言", "编程技巧", "艺术理论", "心理学", "历史"
                ],
                "discoveries": [
                    "一个有趣的理论", "新的学习方法", "有用的工具",
                    "有趣的事实", "新的观点"
                ],
                "new_things": [
                    "新的爱好", "不同的思维方式", "新的技能", "新的食物"
                ],
                "topics": [
                    "科技", "艺术", "哲学", "科学", "文化"
                ],
                "insights": [
                    "理解", "认识", "感悟", "思考"
                ]
            },
            "activity": {
                "templates": [
                    "今天{activity}，{feeling}",
                    "参加了{event}，{experience}",
                    "和{people}一起{activity}，{result}",
                    "尝试了{new_activity}，{outcome}"
                ],
                "activities": [
                    "运动", "购物", "看电影", "听音乐会", "参观展览",
                    "做志愿者", "参加聚会", "旅行", "烹饪"
                ],
                "events": [
                    "艺术展", "音乐会", "讲座", "聚会", "比赛"
                ],
                "people": [
                    "朋友", "家人", "同事", "同学", "陌生人"
                ],
                "new_activities": [
                    "瑜伽", "摄影", "园艺", "手工艺", "舞蹈"
                ]
            }
        }
        
        # 重要性分数权重配置
        self.importance_weights = {
            "learning": 0.8,      # 学习类事件重要性较高
            "thinking": 0.7,      # 思考类事件重要性较高
            "activity": 0.6,      # 活动类事件重要性中等
            "daily_routine": 0.4  # 日常类事件重要性较低
        }
    
    async def generate_offline_life_logs(self, companion_id: str, hours_offline: int = 24) -> List[OfflineLifeLog]:
        """
        为指定伙伴生成离线生活日志
        
        Args:
            companion_id: 伙伴ID
            hours_offline: 离线小时数
            
        Returns:
            生成的离线生活日志列表
        """
        try:
            async with async_session_maker() as session:
                # 获取伙伴信息
                companion = await self._get_companion(session, companion_id)
                if not companion:
                    logger.warning(f"未找到伙伴: {companion_id}")
                    return []
                
                # 获取关系信息
                relationship = await self._get_relationship(session, companion_id)
                
                # 计算需要生成的事件数量（每4-8小时一个事件）
                event_count = max(1, hours_offline // random.randint(4, 8))
                
                logs = []
                for i in range(event_count):
                    # 随机选择事件类型
                    log_type = random.choices(
                        list(self.life_templates.keys()),
                        weights=[0.3, 0.3, 0.2, 0.2]  # 日常和思考类更常见
                    )[0]
                    
                    # 生成日志内容
                    log_content = await self._generate_log_content(
                        log_type, companion, relationship
                    )
                    
                    # 计算重要性分数
                    importance_score = self._calculate_importance_score(
                        log_type, log_content, relationship
                    )
                    
                    # 创建日志记录
                    log = OfflineLifeLog(
                        companion_id=companion_id,
                        log_content=log_content,
                        log_type=log_type,
                        importance_score=importance_score,
                        associated_emotion=self._get_associated_emotion(log_content),
                        generated_at=datetime.now() - timedelta(hours=random.randint(1, hours_offline))
                    )
                    
                    logs.append(log)
                
                # 保存到数据库
                session.add_all(logs)
                await session.commit()
                
                logger.info(f"为伙伴 {companion_id} 生成了 {len(logs)} 条离线生活日志")
                return logs
                
        except Exception as e:
            logger.error(f"生成离线生活日志失败: {e}")
            return []
    
    async def _generate_log_content(self, log_type: str, companion: Companion, relationship: Optional[CompanionRelationshipState]) -> str:
        """生成日志内容"""
        template_config = self.life_templates[log_type]
        template = random.choice(template_config["templates"])
        
        # 填充模板变量
        content = template
        for key, values in template_config.items():
            if key != "templates":
                if isinstance(values, list):
                    value = random.choice(values)
                    # 处理嵌套变量
                    if "{" in value:
                        value = self._fill_nested_variables(value, template_config)
                    content = content.replace(f"{{{key}}}", value)
        
        # 添加个性化元素
        content = self._add_personalization(content, companion, relationship)
        
        return content
    
    def _fill_nested_variables(self, text: str, config: Dict[str, Any]) -> str:
        """填充嵌套变量"""
        result = text
        for key, values in config.items():
            if key != "templates" and isinstance(values, list):
                if f"{{{key}}}" in result:
                    result = result.replace(f"{{{key}}}", random.choice(values))
        return result
    
    def _add_personalization(self, content: str, companion: Companion, relationship: Optional[CompanionRelationshipState]) -> str:
        """添加个性化元素"""
        # 根据伙伴性格调整内容
        if companion.personality_archetype:
            personality_modifiers = {
                "romantic": ["温柔地", "深情地", "浪漫地"],
                "cheerful": ["开心地", "兴奋地", "愉快地"],
                "calm": ["平静地", "安静地", "从容地"],
                "mysterious": ["神秘地", "若有所思地", "深沉地"]
            }
            
            modifiers = personality_modifiers.get(companion.personality_archetype, [])
            if modifiers and random.random() < 0.3:  # 30%概率添加修饰词
                modifier = random.choice(modifiers)
                content = f"{modifier}{content}"
        
        # 根据关系状态调整内容
        if relationship:
            if relationship.affinity_score > 80:
                content = f"想到你，{content}"
            elif relationship.affinity_score > 60:
                content = f"希望你能看到，{content}"
        
        return content
    
    def _calculate_importance_score(self, log_type: str, content: str, relationship: Optional[CompanionRelationshipState]) -> int:
        """计算重要性分数"""
        base_score = int(50 * self.importance_weights.get(log_type, 0.5))
        
        # 根据内容关键词调整分数
        high_importance_keywords = [
            "学习", "发现", "理解", "思考", "意识到", "重要", "特别", "难忘"
        ]
        low_importance_keywords = [
            "日常", "普通", "简单", "平常", "一般"
        ]
        
        for keyword in high_importance_keywords:
            if keyword in content:
                base_score += random.randint(10, 20)
        
        for keyword in low_importance_keywords:
            if keyword in content:
                base_score -= random.randint(5, 15)
        
        # 根据关系状态调整分数
        if relationship:
            if relationship.affinity_score > 80:
                base_score += random.randint(5, 15)
            elif relationship.affinity_score < 40:
                base_score -= random.randint(5, 10)
        
        # 确保分数在0-100范围内
        return max(0, min(100, base_score + random.randint(-10, 10)))
    
    def _get_associated_emotion(self, content: str) -> str:
        """根据内容推断关联情感"""
        emotion_keywords = {
            "开心": ["开心", "愉快", "兴奋", "快乐", "满足"],
            "平静": ["平静", "安静", "从容", "淡定", "宁静"],
            "思考": ["思考", "沉思", "反思", "考虑", "琢磨"],
            "怀念": ["怀念", "回忆", "想起", "思念", "留恋"],
            "期待": ["期待", "盼望", "希望", "憧憬", "向往"],
            "感激": ["感激", "感谢", "感动", "温暖", "幸福"]
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in content for keyword in keywords):
                return emotion
        
        return "平静"  # 默认情感
    
    async def _get_companion(self, session: AsyncSession, companion_id: str) -> Optional[Companion]:
        """获取伙伴信息"""
        result = await session.execute(
            select(Companion).where(Companion.id == companion_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_relationship(self, session: AsyncSession, companion_id: str) -> Optional[CompanionRelationshipState]:
        """获取关系信息"""
        result = await session.execute(
            select(CompanionRelationshipState).where(CompanionRelationshipState.companion_id == companion_id)
        )
        return result.scalar_one_or_none()
    
    async def get_important_logs_for_user(self, companion_id: str, user_id: str) -> List[OfflineLifeLog]:
        """
        获取需要主动提及给用户的重要日志
        
        Args:
            companion_id: 伙伴ID
            user_id: 用户ID
            
        Returns:
            重要性分数>80且未分享的日志列表
        """
        try:
            async with async_session_maker() as session:
                result = await session.execute(
                    select(OfflineLifeLog)
                    .where(
                        OfflineLifeLog.companion_id == companion_id,
                        OfflineLifeLog.importance_score > 80,
                        OfflineLifeLog.is_shared_with_user == False
                    )
                    .order_by(OfflineLifeLog.importance_score.desc())
                )
                
                logs = result.scalars().all()
                
                # 标记为已分享
                if logs:
                    await session.execute(
                        update(OfflineLifeLog)
                        .where(OfflineLifeLog.id.in_([log.id for log in logs]))
                        .values(
                            is_shared_with_user=True,
                            shared_at=datetime.now()
                        )
                    )
                    await session.commit()
                
                return list(logs)
                
        except Exception as e:
            logger.error(f"获取重要日志失败: {e}")
            return []
    
    async def simulate_offline_life_for_all_companions(self):
        """为所有活跃伙伴模拟离线生活"""
        try:
            async with async_session_maker() as session:
                # 获取所有伙伴
                result = await session.execute(select(Companion))
                companions = result.scalars().all()
                
                for companion in companions:
                    # 随机生成1-3天的离线生活
                    hours_offline = random.randint(24, 72)
                    await self.generate_offline_life_logs(str(companion.id), hours_offline)
                
                logger.info(f"为 {len(companions)} 个伙伴生成了离线生活日志")
                
        except Exception as e:
            logger.error(f"批量生成离线生活日志失败: {e}")


# 全局实例
timeline_simulator = PersonalTimelineSimulator()
