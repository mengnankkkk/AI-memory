# -*- coding: utf-8 -*-
"""
任务管理器 - 管理每日任务的创建、检测和完成
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from app.core.redis_client import get_redis
from app.services.redis_utils import redis_affinity_manager

logger = logging.getLogger("task_manager")


# 任务难度定义
TASK_DIFFICULTY = {
    "easy": {"name": "简单", "multiplier": 1.0},
    "medium": {"name": "中等", "multiplier": 1.5},
    "hard": {"name": "困难", "multiplier": 2.0},
    "challenge": {"name": "挑战", "multiplier": 3.0}
}

# 任务类型配置
TASK_CONFIGS = {
    "chat": {
        "max_progress": 10,
        "reward": 5,
        "difficulty": "easy",
        "milestones": [
            {"progress": 5, "bonus": 2},  # 50%完成奖励
            {"progress": 10, "bonus": 3}  # 100%完成奖励
        ]
    },
    "compliment": {
        "max_progress": 1,
        "reward": 8,
        "difficulty": "medium",
        "milestones": []
    },
    "romantic": {
        "max_progress": 1,
        "reward": 15,
        "difficulty": "hard",
        "milestones": []
    },
    "gift": {
        "max_progress": 1,
        "reward": 10,
        "difficulty": "medium",
        "milestones": []
    },
    "morning_greeting": {
        "max_progress": 1,
        "reward": 3,
        "difficulty": "easy",
        "milestones": []
    },
    "night_greeting": {
        "max_progress": 1,
        "reward": 3,
        "difficulty": "easy",
        "milestones": []
    },
    "consecutive_interaction": {
        "max_progress": 7,
        "reward": 20,
        "difficulty": "challenge",
        "milestones": [
            {"progress": 3, "bonus": 5},
            {"progress": 7, "bonus": 10}
        ]
    }
}


class TaskManager:
    """任务管理器 - 管理用户的每日任务"""

    def __init__(self):
        self.task_expiry = 86400  # 任务24小时过期

    def _get_task_key(self, user_id: str, companion_id: int) -> str:
        """获取任务的Redis键"""
        return f"tasks:user:{user_id}:companion:{companion_id}"

    def _get_task_progress_key(self, user_id: str, companion_id: int, task_id: str) -> str:
        """获取任务进度的Redis键"""
        return f"task_progress:user:{user_id}:companion:{companion_id}:task:{task_id}"

    def _get_task_completion_key(self, user_id: str, companion_id: int, task_id: str) -> str:
        """获取任务完成状态的Redis键"""
        return f"task_completion:user:{user_id}:companion:{companion_id}:task:{task_id}"

    async def generate_daily_tasks(
        self,
        user_id: str,
        companion_id: int,
        romance_level: str,
        personality_type: str
    ) -> List[Dict[str, Any]]:
        """
        生成每日任务

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            romance_level: 关系等级
            personality_type: 性格类型

        Returns:
            任务列表
        """
        today = datetime.now().strftime('%Y%m%d')
        current_hour = datetime.now().hour

        # 基础每日任务
        base_tasks = []

        # 聊天任务（有进度）
        chat_task_id = f"daily_chat_{companion_id}_{today}"
        chat_progress = await self.get_task_progress(user_id, companion_id, chat_task_id)
        base_tasks.append({
            "task_id": chat_task_id,
            "task_type": "chat",
            "description": "与伙伴聊天10次",
            "reward_affinity": TASK_CONFIGS["chat"]["reward"],
            "current_progress": chat_progress,
            "max_progress": TASK_CONFIGS["chat"]["max_progress"],
            "difficulty": TASK_CONFIGS["chat"]["difficulty"],
            "completed": chat_progress >= TASK_CONFIGS["chat"]["max_progress"],
            "deadline": (datetime.now() + timedelta(hours=24)).isoformat(),
            "milestones": TASK_CONFIGS["chat"]["milestones"],
            "reward_type": "affinity"
        })

        # 赞美任务
        compliment_task_id = f"daily_compliment_{companion_id}_{today}"
        base_tasks.append({
            "task_id": compliment_task_id,
            "task_type": "compliment",
            "description": "给伙伴一个赞美",
            "reward_affinity": TASK_CONFIGS["compliment"]["reward"],
            "current_progress": 0,
            "max_progress": 1,
            "difficulty": TASK_CONFIGS["compliment"]["difficulty"],
            "completed": await self.is_task_completed(user_id, companion_id, compliment_task_id),
            "deadline": (datetime.now() + timedelta(hours=24)).isoformat(),
            "milestones": [],
            "reward_type": "affinity"
        })

        # 早安问候任务（仅早上6-12点显示）
        if 6 <= current_hour < 12:
            morning_task_id = f"daily_morning_{companion_id}_{today}"
            base_tasks.append({
                "task_id": morning_task_id,
                "task_type": "morning_greeting",
                "description": "说一句早安",
                "reward_affinity": TASK_CONFIGS["morning_greeting"]["reward"],
                "current_progress": 0,
                "max_progress": 1,
                "difficulty": TASK_CONFIGS["morning_greeting"]["difficulty"],
                "completed": await self.is_task_completed(user_id, companion_id, morning_task_id),
                "deadline": (datetime.now().replace(hour=12, minute=0, second=0)).isoformat(),
                "milestones": [],
                "reward_type": "affinity"
            })

        # 晚安问候任务（仅晚上18-24点显示）
        if current_hour >= 18:
            night_task_id = f"daily_night_{companion_id}_{today}"
            base_tasks.append({
                "task_id": night_task_id,
                "task_type": "night_greeting",
                "description": "说一句晚安",
                "reward_affinity": TASK_CONFIGS["night_greeting"]["reward"],
                "current_progress": 0,
                "max_progress": 1,
                "difficulty": TASK_CONFIGS["night_greeting"]["difficulty"],
                "completed": await self.is_task_completed(user_id, companion_id, night_task_id),
                "deadline": (datetime.now().replace(hour=23, minute=59, second=59)).isoformat(),
                "milestones": [],
                "reward_type": "affinity"
            })

        # 根据关系阶段添加特殊任务
        if romance_level in ["romantic", "lover"]:
            romantic_task_id = f"daily_romantic_{companion_id}_{today}"
            base_tasks.append({
                "task_id": romantic_task_id,
                "task_type": "romantic",
                "description": "说一句甜蜜的话",
                "reward_affinity": TASK_CONFIGS["romantic"]["reward"],
                "current_progress": 0,
                "max_progress": 1,
                "difficulty": TASK_CONFIGS["romantic"]["difficulty"],
                "completed": await self.is_task_completed(user_id, companion_id, romantic_task_id),
                "deadline": (datetime.now() + timedelta(hours=24)).isoformat(),
                "milestones": [],
                "reward_type": "affinity"
            })

        # 连续互动任务（挑战级）
        consecutive_task_id = f"weekly_consecutive_{companion_id}_{datetime.now().strftime('%Y%W')}"
        consecutive_progress = await self.get_consecutive_days(user_id, companion_id)
        base_tasks.append({
            "task_id": consecutive_task_id,
            "task_type": "consecutive_interaction",
            "description": "连续7天与伙伴互动",
            "reward_affinity": TASK_CONFIGS["consecutive_interaction"]["reward"],
            "reward_coins": 100,  # 额外金币奖励
            "current_progress": consecutive_progress,
            "max_progress": 7,
            "difficulty": TASK_CONFIGS["consecutive_interaction"]["difficulty"],
            "completed": consecutive_progress >= 7,
            "deadline": (datetime.now() + timedelta(days=7 - datetime.now().weekday())).isoformat(),
            "milestones": TASK_CONFIGS["consecutive_interaction"]["milestones"],
            "reward_type": "mixed"  # 混合奖励
        })

        return base_tasks

    async def is_task_completed(self, user_id: str, companion_id: int, task_id: str) -> bool:
        """
        检查任务是否已完成

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            task_id: 任务ID

        Returns:
            是否已完成
        """
        try:
            redis = await get_redis()
            key = self._get_task_completion_key(user_id, companion_id, task_id)
            result = await redis.get(key)
            return result == "1" if result else False
        except Exception as e:
            logger.error(f"[TaskManager] 检查任务完成状态失败: {e}")
            return False

    async def get_task_progress(self, user_id: str, companion_id: int, task_id: str) -> int:
        """
        获取任务进度

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            task_id: 任务ID

        Returns:
            当前进度
        """
        try:
            redis = await get_redis()
            key = self._get_task_progress_key(user_id, companion_id, task_id)
            result = await redis.get(key)
            return int(result) if result else 0
        except Exception as e:
            logger.error(f"[TaskManager] 获取任务进度失败: {e}")
            return 0

    async def update_task_progress(
        self,
        user_id: str,
        companion_id: int,
        task_id: str,
        increment: int = 1
    ) -> Dict[str, Any]:
        """
        更新任务进度

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            task_id: 任务ID
            increment: 增加的进度

        Returns:
            更新结果（包含里程碑奖励信息）
        """
        try:
            redis = await get_redis()
            key = self._get_task_progress_key(user_id, companion_id, task_id)
            new_progress = await redis.incrby(key, increment)
            await redis.expire(key, self.task_expiry)

            # 检查里程碑奖励
            task_type = task_id.split('_')[1]  # 从task_id解析任务类型
            config = TASK_CONFIGS.get(task_type, {})
            milestones = config.get("milestones", [])

            milestone_rewards = []
            for milestone in milestones:
                milestone_progress = milestone["progress"]
                # 检查是否刚好达到里程碑（避免重复奖励）
                if new_progress == milestone_progress:
                    milestone_rewards.append({
                        "progress": milestone_progress,
                        "bonus": milestone["bonus"],
                        "type": "affinity"
                    })

            return {
                "current_progress": new_progress,
                "max_progress": config.get("max_progress", 1),
                "milestone_rewards": milestone_rewards
            }

        except Exception as e:
            logger.error(f"[TaskManager] 更新任务进度失败: {e}")
            return {"current_progress": 0, "max_progress": 1, "milestone_rewards": []}

    async def get_consecutive_days(self, user_id: str, companion_id: int) -> int:
        """
        获取连续互动天数

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID

        Returns:
            连续天数
        """
        try:
            redis = await get_redis()
            key = f"consecutive_days:user:{user_id}:companion:{companion_id}"
            result = await redis.get(key)
            return int(result) if result else 0
        except Exception as e:
            logger.error(f"[TaskManager] 获取连续天数失败: {e}")
            return 0

    async def update_consecutive_days(self, user_id: str, companion_id: int) -> int:
        """
        更新连续互动天数

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID

        Returns:
            当前连续天数
        """
        try:
            redis = await get_redis()
            today = datetime.now().strftime('%Y%m%d')
            last_interaction_key = f"last_interaction_date:user:{user_id}:companion:{companion_id}"
            consecutive_key = f"consecutive_days:user:{user_id}:companion:{companion_id}"

            last_date = await redis.get(last_interaction_key)

            if not last_date:
                # 首次互动
                await redis.set(consecutive_key, "1")
                await redis.set(last_interaction_key, today)
                await redis.expire(consecutive_key, 86400 * 8)  # 8天过期
                await redis.expire(last_interaction_key, 86400 * 8)
                return 1
            else:
                last_date_str = last_date.decode() if isinstance(last_date, bytes) else last_date
                yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

                if last_date_str == today:
                    # 今天已经互动过，返回当前连续天数
                    current = await redis.get(consecutive_key)
                    return int(current) if current else 1
                elif last_date_str == yesterday:
                    # 昨天互动过，连续天数+1
                    new_count = await redis.incr(consecutive_key)
                    await redis.set(last_interaction_key, today)
                    await redis.expire(consecutive_key, 86400 * 8)
                    await redis.expire(last_interaction_key, 86400 * 8)
                    return new_count
                else:
                    # 中断了，重置为1
                    await redis.set(consecutive_key, "1")
                    await redis.set(last_interaction_key, today)
                    await redis.expire(consecutive_key, 86400 * 8)
                    await redis.expire(last_interaction_key, 86400 * 8)
                    return 1

        except Exception as e:
            logger.error(f"[TaskManager] 更新连续天数失败: {e}")
            return 0

    async def complete_task(
        self,
        user_id: str,
        companion_id: int,
        task_id: str
    ) -> Dict[str, Any]:
        """
        完成任务

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            task_id: 任务ID

        Returns:
            完成结果（包括奖励信息）
        """
        try:
            # 检查任务是否已完成
            if await self.is_task_completed(user_id, companion_id, task_id):
                return {
                    "success": False,
                    "message": "任务已经完成过了",
                    "reward": 0
                }

            # 获取任务信息（从任务ID解析奖励）
            reward = self._get_task_reward(task_id)

            if reward == 0:
                return {
                    "success": False,
                    "message": "无效的任务ID",
                    "reward": 0
                }

            # 标记任务为已完成
            redis = await get_redis()
            key = self._get_task_completion_key(user_id, companion_id, task_id)
            await redis.setex(key, self.task_expiry, "1")

            # 更新Redis好感度（用于自动完成任务的奖励）
            await redis_affinity_manager.update_affinity(
                user_id=user_id,
                companion_id=companion_id,
                affinity_change=reward,
                interaction_type="task"
            )

            logger.info(f"[TaskManager] 用户 {user_id} 完成任务 {task_id}，获得 {reward} 好感度")

            return {
                "success": True,
                "message": f"任务完成！获得 {reward} 好感度",
                "reward": reward,
                "task_id": task_id
            }

        except Exception as e:
            logger.error(f"[TaskManager] 完成任务失败: {e}")
            return {
                "success": False,
                "message": "服务器错误",
                "reward": 0
            }

    def _get_task_reward(self, task_id: str) -> int:
        """
        根据任务ID获取奖励数量

        Args:
            task_id: 任务ID

        Returns:
            好感度奖励
        """
        # 从任务ID解析任务类型
        if "chat" in task_id:
            return 5
        elif "compliment" in task_id:
            return 8
        elif "romantic" in task_id:
            return 15
        elif "morning" in task_id or "morning_greeting" in task_id:
            return 3
        elif "night" in task_id or "night_greeting" in task_id:
            return 3
        elif "gift" in task_id:
            return 10
        else:
            logger.warning(f"[TaskManager] 未知的任务ID类型: {task_id}")
            return 0

    def _get_interaction_counter_key(self, user_id: str, companion_id: int, interaction_type: str) -> str:
        """获取互动计数器的Redis键"""
        today = datetime.now().strftime('%Y%m%d')
        return f"interaction_counter:user:{user_id}:companion:{companion_id}:type:{interaction_type}:date:{today}"

    async def increment_interaction_count(
        self,
        user_id: str,
        companion_id: int,
        interaction_type: str
    ) -> int:
        """
        增加互动计数

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            interaction_type: 互动类型 (chat, compliment, romantic, gift)

        Returns:
            当前计数
        """
        try:
            redis = await get_redis()
            key = self._get_interaction_counter_key(user_id, companion_id, interaction_type)
            count = await redis.incr(key)
            # 设置过期时间为当天结束
            await redis.expire(key, self.task_expiry)
            return count
        except Exception as e:
            logger.error(f"[TaskManager] 增加互动计数失败: {e}")
            return 0

    async def get_interaction_count(
        self,
        user_id: str,
        companion_id: int,
        interaction_type: str
    ) -> int:
        """
        获取互动计数

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            interaction_type: 互动类型

        Returns:
            当前计数
        """
        try:
            redis = await get_redis()
            key = self._get_interaction_counter_key(user_id, companion_id, interaction_type)
            result = await redis.get(key)
            return int(result) if result else 0
        except Exception as e:
            logger.error(f"[TaskManager] 获取互动计数失败: {e}")
            return 0

    async def check_and_complete_task_automatically(
        self,
        user_id: str,
        companion_id: int,
        interaction_type: str,
        message_content: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        检查并自动完成任务

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            interaction_type: 互动类型
            message_content: 消息内容（用于情感分析）

        Returns:
            如果任务被自动完成，返回完成结果；否则返回None
        """
        try:
            today = datetime.now().strftime('%Y%m%d')
            task_id = f"daily_{interaction_type}_{companion_id}_{today}"

            # 特殊处理：早安和晚安任务
            if interaction_type in ["morning_greeting", "night_greeting"]:
                # 检测消息中是否包含早安/晚安
                if interaction_type == "morning_greeting" and message_content:
                    if not any(keyword in message_content for keyword in ["早安", "早上好", "早", "Good morning"]):
                        logger.debug(f"[TaskManager] 消息不包含早安关键词: {message_content}")
                        return None
                elif interaction_type == "night_greeting" and message_content:
                    keywords = ["晚安", "晚上好", "Good night"]
                    has_keyword = any(keyword in message_content for keyword in keywords)
                    logger.info(f"[TaskManager] 检测晚安关键词: message='{message_content}', has_keyword={has_keyword}")
                    if not has_keyword:
                        logger.debug(f"[TaskManager] 消息不包含晚安关键词")
                        return None

            # 检查任务是否已完成
            is_completed = await self.is_task_completed(user_id, companion_id, task_id)
            if is_completed:
                logger.debug(f"[TaskManager] 任务已完成，跳过: task_id={task_id}")
                return None
            else:
                logger.info(f"[TaskManager] 任务未完成，准备自动完成: task_id={task_id}, interaction_type={interaction_type}")

            # 更新连续互动天数（仅聊天类任务）
            if interaction_type == "chat":
                await self.update_consecutive_days(user_id, companion_id)

            # 检查是否满足自动完成条件
            should_complete = False
            progress_result = None

            if interaction_type == "chat":
                # 聊天任务：更新进度
                progress_result = await self.update_task_progress(user_id, companion_id, task_id)
                should_complete = progress_result["current_progress"] >= progress_result["max_progress"]

                # 处理里程碑奖励
                if progress_result["milestone_rewards"]:
                    for milestone in progress_result["milestone_rewards"]:
                        logger.info(f"[TaskManager] 达成里程碑奖励：{milestone}")

            elif interaction_type == "compliment" and message_content:
                # 赞美任务：检测赞美关键词
                should_complete = self._detect_compliment(message_content)
            elif interaction_type == "romantic" and message_content:
                # 浪漫任务：检测浪漫关键词
                should_complete = self._detect_romantic(message_content)
            elif interaction_type in ["gift", "morning_greeting", "night_greeting"]:
                # 礼物、早安、晚安任务：触发即完成
                should_complete = True

            if should_complete:
                result = await self.complete_task(user_id, companion_id, task_id)
                if result["success"]:
                    logger.info(f"[TaskManager] 自动完成任务 {task_id}，用户: {user_id}")

                    # 添加里程碑奖励到结果中
                    if progress_result and progress_result.get("milestone_rewards"):
                        result["milestone_rewards"] = progress_result["milestone_rewards"]

                    return result

            # 即使没有完成，也返回进度更新信息
            if progress_result and progress_result.get("milestone_rewards"):
                return {
                    "success": False,
                    "message": f"任务进度: {progress_result['current_progress']}/{progress_result['max_progress']}",
                    "reward": 0,
                    "progress": progress_result["current_progress"],
                    "max_progress": progress_result["max_progress"],
                    "milestone_rewards": progress_result["milestone_rewards"]
                }

            return None

        except Exception as e:
            logger.error(f"[TaskManager] 自动完成任务检测失败: {e}")
            return None

    def _detect_compliment(self, message: str) -> bool:
        """检测消息是否包含赞美词汇"""
        compliment_keywords = [
            "漂亮", "美丽", "可爱", "帅", "好看", "迷人", "优雅", "温柔",
            "聪明", "智慧", "才华", "优秀", "出色", "厉害", "棒", "赞",
            "喜欢", "爱", "欣赏", "佩服", "崇拜", "仰慕", "倾心", "心动"
        ]
        message_lower = message.lower()
        return any(keyword in message for keyword in compliment_keywords)

    def _detect_romantic(self, message: str) -> bool:
        """检测消息是否包含浪漫词汇"""
        romantic_keywords = [
            "想你", "念你", "思念", "挂念", "牵挂", "想念",
            "陪你", "陪伴", "守护", "保护", "珍惜", "呵护",
            "喜欢你", "爱你", "爱慕", "倾心", "心动", "心跳", "脸红",
            "亲爱的", "宝贝", "甜心", "亲", "么么哒", "抱抱", "亲亲",
            "浪漫", "甜蜜", "温馨", "幸福", "美好", "梦幻"
        ]
        message_lower = message.lower()
        return any(keyword in message for keyword in romantic_keywords)

    async def check_task_completion_conditions(
        self,
        user_id: str,
        companion_id: int,
        task_type: str,
        interaction_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        检查任务完成条件

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
            task_type: 任务类型
            interaction_data: 交互数据（如聊天内容、时长等）

        Returns:
            是否满足完成条件
        """
        # TODO: 这里可以实现更复杂的任务完成条件检测
        # 例如：
        # - chat任务：检测聊天时长是否>10分钟
        # - compliment任务：检测消息中是否包含赞美词汇
        # - romantic任务：检测消息情感倾向

        # 目前简化为直接返回True，由前端用户手动触发
        return True

    async def reset_daily_tasks(self, user_id: str, companion_id: int) -> None:
        """
        重置每日任务（每天0点自动调用）

        Args:
            user_id: 用户ID
            companion_id: 伙伴ID
        """
        try:
            redis = await get_redis()
            # 获取今天的所有任务键
            pattern = self._get_task_completion_key(user_id, companion_id, "*")
            keys = await redis.keys(pattern)

            if keys:
                await redis.delete(*keys)
                logger.info(f"[TaskManager] 已重置用户 {user_id} 和伙伴 {companion_id} 的每日任务")

        except Exception as e:
            logger.error(f"[TaskManager] 重置每日任务失败: {e}")


# 创建全局任务管理器实例
task_manager = TaskManager()
