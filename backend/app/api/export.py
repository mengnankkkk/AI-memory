"""
数据导出与备份API
提供对话记录导出、用户数据备份、统计报告生成等功能
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import get_db
from app.models.chat_session import ChatSession
from app.models.companion import Companion
from app.services.analytics import analytics_service
from typing import List, Optional
import csv
import json
import io
from datetime import datetime, timedelta
import zipfile
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/export", tags=["export"])

@router.get("/conversations/csv")
async def export_conversations_csv(
    user_id: Optional[int] = Query(None),
    companion_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """导出对话记录为CSV"""
    try:
        # 构建查询条件
        conditions = []
        if user_id:
            conditions.append(ChatSession.user_id == user_id)
        if companion_id:
            conditions.append(ChatSession.companion_id == companion_id)
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            conditions.append(ChatSession.created_at >= start_dt)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            conditions.append(ChatSession.created_at <= end_dt)
        
        # 查询对话记录
        query = select(ChatSession)
        if conditions:
            query = query.where(and_(*conditions))
        query = query.order_by(ChatSession.created_at.desc())
        
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        # 生成CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow([
            "会话ID", "用户ID", "伙伴ID", "创建时间", "最后更新", 
            "消息总数", "质量评分", "状态"
        ])
        
        # 写入数据
        for session in sessions:
            writer.writerow([
                session.id,
                session.user_id,
                session.companion_id,
                session.created_at.isoformat(),
                session.updated_at.isoformat(),
                len(session.messages) if session.messages else 0,
                session.quality_score or "N/A",
                session.status
            ])
        
        output.seek(0)
        
        # 返回CSV文件
        filename = f"conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"导出对话记录失败: {e}")
        raise HTTPException(status_code=500, detail="导出失败")

@router.get("/conversations/json")
async def export_conversations_json(
    user_id: Optional[int] = Query(None),
    companion_id: Optional[int] = Query(None),
    include_messages: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """导出对话记录为JSON"""
    try:
        # 构建查询条件
        conditions = []
        if user_id:
            conditions.append(ChatSession.user_id == user_id)
        if companion_id:
            conditions.append(ChatSession.companion_id == companion_id)
        
        query = select(ChatSession)
        if conditions:
            query = query.where(and_(*conditions))
        query = query.order_by(ChatSession.created_at.desc())
        
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        # 构建导出数据
        export_data = {
            "export_time": datetime.now().isoformat(),
            "total_sessions": len(sessions),
            "sessions": []
        }
        
        for session in sessions:
            session_data = {
                "id": session.id,
                "user_id": session.user_id,
                "companion_id": session.companion_id,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "quality_score": session.quality_score,
                "status": session.status
            }
            
            if include_messages and session.messages:
                session_data["messages"] = [
                    {
                        "role": msg.get("role"),
                        "content": msg.get("content"),
                        "timestamp": msg.get("timestamp")
                    }
                    for msg in session.messages
                ]
            
            export_data["sessions"].append(session_data)
        
        # 生成JSON
        json_content = json.dumps(export_data, ensure_ascii=False, indent=2)
        
        filename = f"conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        return StreamingResponse(
            io.BytesIO(json_content.encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"导出JSON失败: {e}")
        raise HTTPException(status_code=500, detail="导出失败")

@router.get("/analytics/report")
async def export_analytics_report(
    days: int = Query(30, ge=1, le=365),
    format: str = Query("json", regex="^(json|csv)$")
):
    """导出分析报告"""
    try:
        # 获取分析数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 这里应该从analytics服务获取实际数据
        # 为了示例，我们生成模拟数据
        report_data = {
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "summary": {
                "total_conversations": 150,
                "total_messages": 1250,
                "avg_quality_score": 4.2,
                "active_users": 45,
                "active_companions": 32
            },
            "daily_stats": [
                {
                    "date": (start_date + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "conversations": 5 + (i % 10),
                    "messages": 40 + (i % 50),
                    "avg_quality": 3.8 + (i % 3) * 0.2
                }
                for i in range(days)
            ],
            "top_companions": [
                {"id": 1, "name": "AI助手", "conversation_count": 45},
                {"id": 2, "name": "学习伙伴", "conversation_count": 38},
                {"id": 3, "name": "创作助手", "conversation_count": 32}
            ]
        }
        
        if format == "json":
            json_content = json.dumps(report_data, ensure_ascii=False, indent=2)
            filename = f"analytics_report_{days}days_{datetime.now().strftime('%Y%m%d')}.json"
            return StreamingResponse(
                io.BytesIO(json_content.encode('utf-8')),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:  # CSV format
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入汇总信息
            writer.writerow(["报告摘要"])
            writer.writerow(["指标", "数值"])
            for key, value in report_data["summary"].items():
                writer.writerow([key, value])
            
            writer.writerow([])  # 空行
            writer.writerow(["每日统计"])
            writer.writerow(["日期", "对话数", "消息数", "平均质量"])
            for stat in report_data["daily_stats"]:
                writer.writerow([stat["date"], stat["conversations"], 
                               stat["messages"], stat["avg_quality"]])
            
            output.seek(0)
            filename = f"analytics_report_{days}days_{datetime.now().strftime('%Y%m%d')}.csv"
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode('utf-8-sig')),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
    except Exception as e:
        logger.error(f"导出分析报告失败: {e}")
        raise HTTPException(status_code=500, detail="导出报告失败")

@router.get("/backup/full")
async def export_full_backup(
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """导出用户完整数据备份"""
    try:
        # 查询用户的所有数据
        # 伙伴数据
        companions_result = await db.execute(
            select(Companion).where(Companion.user_id == user_id)
        )
        companions = companions_result.scalars().all()
        
        # 对话数据
        sessions_result = await db.execute(
            select(ChatSession).where(ChatSession.user_id == user_id)
        )
        sessions = sessions_result.scalars().all()
        
        # 创建ZIP文件
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 添加伙伴数据
            companions_data = []
            for companion in companions:
                companions_data.append({
                    "id": companion.id,
                    "name": companion.name,
                    "avatar": companion.avatar,
                    "personality": companion.personality,
                    "custom_prompt": companion.custom_prompt,
                    "prompt_version": companion.prompt_version,
                    "created_at": companion.created_at.isoformat(),
                    "updated_at": companion.updated_at.isoformat()
                })
            
            zip_file.writestr(
                "companions.json",
                json.dumps(companions_data, ensure_ascii=False, indent=2)
            )
            
            # 添加对话数据
            sessions_data = []
            for session in sessions:
                sessions_data.append({
                    "id": session.id,
                    "companion_id": session.companion_id,
                    "messages": session.messages,
                    "quality_score": session.quality_score,
                    "status": session.status,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat()
                })
            
            zip_file.writestr(
                "conversations.json",
                json.dumps(sessions_data, ensure_ascii=False, indent=2)
            )
            
            # 添加备份信息
            backup_info = {
                "user_id": user_id,
                "backup_time": datetime.now().isoformat(),
                "companions_count": len(companions),
                "sessions_count": len(sessions),
                "version": "1.0"
            }
            
            zip_file.writestr(
                "backup_info.json",
                json.dumps(backup_info, ensure_ascii=False, indent=2)
            )
        
        zip_buffer.seek(0)
        
        filename = f"backup_user_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        return StreamingResponse(
            io.BytesIO(zip_buffer.getvalue()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"导出完整备份失败: {e}")
        raise HTTPException(status_code=500, detail="备份失败")
