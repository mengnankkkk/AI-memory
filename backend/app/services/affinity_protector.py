"""
容错机制与边界保护
防止好感度异常波动,提供平滑的好感度调整体验
"""
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import math


@dataclass
class AffinityHistory:
    """好感度历史记录"""
    timestamp: datetime
    change: int
    reason: str
    before_score: int
    after_score: int


@dataclass
class ProtectionResult:
    """保护机制处理结果"""
    original_change: int  # 原始变化值
    adjusted_change: int  # 调整后的变化值
    applied_rate: float  # 应用的速率
    protection_reason: str  # 保护原因
    warnings: List[str]  # 警告信息


class AffinityProtector:
    """好感度保护器"""

    # 边界配置
    ABSOLUTE_MIN = 0
    ABSOLUTE_MAX = 1000
    SAFE_MIN = 50
    SAFE_MAX = 950
    WARNING_THRESHOLD = 100  # 单次变化警告阈值

    # 速率配置
    NORMAL_RATE = 1.0
    ACCELERATED_RATE = 1.3  # 低分时加速增长
    DECELERATED_RATE = 0.7  # 高分时减缓增长
    PROTECTED_RATE = 0.4  # 边界保护速率
    RECOVERY_RATE = 1.2  # 恢复速率(从极低分恢复时)

    # 单次调整限制
    MAX_SINGLE_INCREASE = 50
    MAX_SINGLE_DECREASE = 30
    CRITICAL_DECREASE = 20  # 严重违规最大减少

    # 历史缓冲配置
    HISTORY_BUFFER_SIZE = 20  # 保留最近20条记录
    RAPID_CHANGE_WINDOW = timedelta(minutes=5)  # 快速变化检测窗口
    RAPID_CHANGE_THRESHOLD = 100  # 5分钟内变化超过此值视为异常

    def __init__(self):
        self.history: List[AffinityHistory] = []

    def protect_and_adjust(
        self,
        current_score: int,
        raw_change: int,
        reason: str = ""
    ) -> ProtectionResult:
        """
        应用保护机制并调整好感度变化

        Args:
            current_score: 当前好感度分数
            raw_change: 原始变化值
            reason: 变化原因

        Returns:
            ProtectionResult: 保护处理结果
        """
        warnings = []
        adjusted_change = raw_change
        applied_rate = self.NORMAL_RATE
        protection_reason = "normal"

        # 1. 单次变化限制
        if raw_change > 0:
            if raw_change > self.MAX_SINGLE_INCREASE:
                adjusted_change = self.MAX_SINGLE_INCREASE
                warnings.append(f"单次增加过大({raw_change}),已限制为{self.MAX_SINGLE_INCREASE}")
        else:
            if raw_change < -self.MAX_SINGLE_DECREASE:
                adjusted_change = max(raw_change, -self.MAX_SINGLE_DECREASE)
                warnings.append(f"单次减少过大({raw_change}),已限制为{-self.MAX_SINGLE_DECREASE}")

        # 2. 快速变化检测
        rapid_change = self._detect_rapid_change()
        if rapid_change > self.RAPID_CHANGE_THRESHOLD:
            adjusted_change = int(adjusted_change * 0.5)
            warnings.append(f"检测到短时间内大幅波动,已降低调整速率")
            protection_reason = "rapid_change_protection"

        # 3. 根据当前分数调整速率
        if current_score < self.SAFE_MIN:
            # 低分保护:加速恢复正增长,减缓负增长
            if adjusted_change > 0:
                applied_rate = self.RECOVERY_RATE
                adjusted_change = int(adjusted_change * applied_rate)
                protection_reason = "low_score_recovery"
            else:
                applied_rate = self.PROTECTED_RATE
                adjusted_change = int(adjusted_change * applied_rate)
                warnings.append("好感度偏低,已减缓负面影响")
                protection_reason = "low_score_protection"

        elif current_score > self.SAFE_MAX:
            # 高分保护:减缓正增长,保持负增长
            if adjusted_change > 0:
                applied_rate = self.DECELERATED_RATE
                adjusted_change = int(adjusted_change * applied_rate)
                warnings.append("好感度已很高,增长速度放缓")
                protection_reason = "high_score_deceleration"

        elif current_score < 250:
            # 中低分:加速正增长
            if adjusted_change > 0:
                applied_rate = self.ACCELERATED_RATE
                adjusted_change = int(adjusted_change * applied_rate)
                protection_reason = "acceleration"

        # 4. 边界检查:确保不超出绝对边界
        new_score = current_score + adjusted_change
        if new_score < self.ABSOLUTE_MIN:
            adjusted_change = self.ABSOLUTE_MIN - current_score
            warnings.append("已达到好感度最低值")
            protection_reason = "absolute_min_boundary"
        elif new_score > self.ABSOLUTE_MAX:
            adjusted_change = self.ABSOLUTE_MAX - current_score
            warnings.append("已达到好感度最高值")
            protection_reason = "absolute_max_boundary"

        # 5. 记录历史
        self._add_history(
            current_score, adjusted_change, reason
        )

        return ProtectionResult(
            original_change=raw_change,
            adjusted_change=adjusted_change,
            applied_rate=applied_rate,
            protection_reason=protection_reason,
            warnings=warnings
        )

    def _detect_rapid_change(self) -> int:
        """检测快速变化"""
        if len(self.history) < 2:
            return 0

        now = datetime.now()
        recent_changes = [
            record.change
            for record in self.history
            if now - record.timestamp < self.RAPID_CHANGE_WINDOW
        ]

        return sum(abs(change) for change in recent_changes)

    def _add_history(self, before_score: int, change: int, reason: str):
        """添加历史记录"""
        after_score = before_score + change
        record = AffinityHistory(
            timestamp=datetime.now(),
            change=change,
            reason=reason,
            before_score=before_score,
            after_score=after_score
        )

        self.history.append(record)

        # 保持缓冲区大小
        if len(self.history) > self.HISTORY_BUFFER_SIZE:
            self.history.pop(0)

    def get_recent_trend(self, window_size: int = 5) -> str:
        """
        获取最近的好感度趋势

        Returns:
            "rising" | "falling" | "stable" | "volatile"
        """
        if len(self.history) < window_size:
            return "stable"

        recent = self.history[-window_size:]
        changes = [record.change for record in recent]

        # 计算总变化和波动性
        total_change = sum(changes)
        volatility = sum(abs(change) for change in changes)

        # 判断趋势
        if volatility > 50:
            return "volatile"  # 波动大
        elif total_change > 10:
            return "rising"  # 上升
        elif total_change < -10:
            return "falling"  # 下降
        else:
            return "stable"  # 稳定

    def suggest_recovery_action(self, current_score: int) -> str:
        """建议恢复行动"""
        if current_score < self.SAFE_MIN:
            return "好感度偏低,建议通过积极互动、赞美、分享来提升关系"
        elif current_score < 250:
            return "关系还在初级阶段,继续保持良好互动可以加速提升好感度"
        elif current_score > self.SAFE_MAX:
            return "好感度已经很高,重点维护和深化关系质量"
        else:
            return "好感度正常,保持当前互动方式即可"

    def get_history_summary(self) -> Dict:
        """获取历史统计摘要"""
        if not self.history:
            return {
                "total_interactions": 0,
                "total_increase": 0,
                "total_decrease": 0,
                "net_change": 0,
                "average_change": 0,
            }

        total_increase = sum(r.change for r in self.history if r.change > 0)
        total_decrease = sum(r.change for r in self.history if r.change < 0)
        net_change = sum(r.change for r in self.history)
        average_change = net_change / len(self.history)

        return {
            "total_interactions": len(self.history),
            "total_increase": total_increase,
            "total_decrease": abs(total_decrease),
            "net_change": net_change,
            "average_change": round(average_change, 2),
            "trend": self.get_recent_trend(),
        }


class SmoothAdjuster:
    """平滑调整器 - 使好感度变化更自然"""

    @staticmethod
    def smooth_transition(
        current_score: int,
        target_change: int,
        smoothness: float = 0.5
    ) -> int:
        """
        平滑过渡算法

        Args:
            current_score: 当前分数
            target_change: 目标变化值
            smoothness: 平滑系数 0-1,越大越平滑

        Returns:
            平滑后的变化值
        """
        # 使用对数函数实现递减效应
        if target_change > 0:
            # 分数越高,增长越慢
            factor = 1 - (current_score / 1000) * smoothness
            return int(target_change * max(factor, 0.3))
        else:
            # 分数越低,下降越慢
            factor = 1 - ((1000 - current_score) / 1000) * smoothness
            return int(target_change * max(factor, 0.3))

    @staticmethod
    def apply_decay(change: int, decay_rate: float = 0.95) -> int:
        """
        应用衰减效果
        用于连续相同行为的递减效应
        """
        return int(change * decay_rate)

    @staticmethod
    def calculate_bonus(
        current_level: str,
        interaction_count: int
    ) -> int:
        """
        计算里程碑奖励
        在特定交互次数给予额外好感度
        """
        milestones = {
            10: 5,
            50: 10,
            100: 20,
            200: 30,
            500: 50,
        }

        return milestones.get(interaction_count, 0)


# 全局保护器实例(可以根据需要创建多个)
global_protector = AffinityProtector()
