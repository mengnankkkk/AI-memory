"""
时间线调度器
负责定时执行离线生活模拟任务
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from app.services.personal_timeline_simulator import timeline_simulator

logger = logging.getLogger(__name__)


class TimelineScheduler:
    """时间线调度器"""
    
    def __init__(self):
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.execution_hour = 2  # 每天凌晨2点执行
    
    async def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("时间线调度器已在运行")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._run_scheduler())
        logger.info("时间线调度器已启动")
    
    async def stop(self):
        """停止调度器"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("时间线调度器已停止")
    
    async def _run_scheduler(self):
        """运行调度器主循环"""
        while self.is_running:
            try:
                # 计算到下一个执行时间（每天凌晨2点）
                now = datetime.now()
                next_execution = now.replace(hour=self.execution_hour, minute=0, second=0, microsecond=0)
                
                # 如果今天已经过了执行时间，则设置为明天
                if now >= next_execution:
                    next_execution += timedelta(days=1)
                
                delay_seconds = (next_execution - now).total_seconds()
                
                logger.info(f"时间线调度器将在 {next_execution.strftime('%Y-%m-%d %H:%M')} 执行，等待 {delay_seconds/3600:.1f} 小时")
                
                # 等待到执行时间
                await asyncio.sleep(delay_seconds)
                
                # 执行离线生活模拟
                await self._execute_offline_simulation()
                
            except asyncio.CancelledError:
                logger.info("时间线调度器被取消")
                break
            except Exception as e:
                logger.error(f"时间线调度器执行出错: {e}")
                # 出错后等待1小时再重试
                await asyncio.sleep(3600)
    
    async def _execute_offline_simulation(self):
        """执行离线生活模拟"""
        try:
            logger.info("开始执行离线生活模拟...")
            await timeline_simulator.simulate_offline_life_for_all_companions()
            logger.info("离线生活模拟完成")
        except Exception as e:
            logger.error(f"执行离线生活模拟失败: {e}")
    
    async def trigger_immediate_simulation(self):
        """立即触发一次模拟（用于测试）"""
        try:
            logger.info("手动触发离线生活模拟...")
            await self._execute_offline_simulation()
            logger.info("手动触发完成")
        except Exception as e:
            logger.error(f"手动触发失败: {e}")
    
    def set_execution_hour(self, hour: int):
        """设置执行时间（24小时制）"""
        if 0 <= hour <= 23:
            self.execution_hour = hour
            logger.info(f"时间线调度器执行时间设置为每天 {hour:02d}:00")
        else:
            logger.warning("无效的执行时间，应为0-23")


# 全局实例
timeline_scheduler = TimelineScheduler()
