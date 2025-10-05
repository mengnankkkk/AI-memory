from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.companion import Companion
from app.api.schemas import CompanionCreate, CompanionResponse
from app.core.prompts import get_greeting
from typing import List, Optional

router = APIRouter(prefix="/companions", tags=["companions"])


@router.post("/", response_model=CompanionResponse)
async def create_companion(
    companion_data: CompanionCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建AI伙伴"""
    # 创建伙伴实例
    companion = Companion(
        user_id=companion_data.user_id,
        name=companion_data.name,
        avatar_id=companion_data.avatar_id,
        personality_archetype=companion_data.personality_archetype,
        custom_greeting=companion_data.custom_greeting
    )

    db.add(companion)
    await db.commit()
    await db.refresh(companion)

    # 生成问候语
    greeting = get_greeting(companion.name, companion.personality_archetype)

    return CompanionResponse(
        id=companion.id,
        user_id=companion.user_id,
        name=companion.name,
        avatar_id=companion.avatar_id,
        personality_archetype=companion.personality_archetype,
        custom_greeting=companion.custom_greeting,
        greeting=greeting
    )


@router.get("/{companion_id}", response_model=CompanionResponse)
async def get_companion(
    companion_id: int,
    user_id: Optional[str] = None,  # 可选的用户验证
    db: AsyncSession = Depends(get_db)
):
    """获取伙伴信息"""
    query = select(Companion).where(Companion.id == companion_id)
    
    # 如果提供了user_id，添加用户验证
    if user_id:
        query = query.where(Companion.user_id == user_id)
    
    result = await db.execute(query)
    companion = result.scalar_one_or_none()

    if not companion:
        raise HTTPException(status_code=404, detail="伙伴不存在或无权访问")

    greeting = get_greeting(companion.name, companion.personality_archetype)

    return CompanionResponse(
        id=companion.id,
        user_id=companion.user_id,
        name=companion.name,
        avatar_id=companion.avatar_id,
        personality_archetype=companion.personality_archetype,
        custom_greeting=companion.custom_greeting,
        greeting=greeting
    )


@router.delete("/{companion_id}")
async def delete_companion(
    companion_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除伙伴"""
    result = await db.execute(
        select(Companion).where(Companion.id == companion_id)
    )
    companion = result.scalar_one_or_none()

    if not companion:
        raise HTTPException(status_code=404, detail="伙伴不存在")

    await db.delete(companion)
    await db.commit()

    return {"message": "伙伴已删除"}


@router.get("/user/{user_id}", response_model=List[CompanionResponse])
async def get_user_companions(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取用户的所有伙伴"""
    result = await db.execute(
        select(Companion).where(Companion.user_id == user_id)
    )
    companions = result.scalars().all()

    if not companions:
        return []

    response_companions = []
    for companion in companions:
        greeting = get_greeting(
            companion.name,
            companion.personality_archetype
        )

        response_companions.append(CompanionResponse(
            id=companion.id,
            user_id=companion.user_id,
            name=companion.name,
            avatar_id=companion.avatar_id,
            personality_archetype=companion.personality_archetype,
            custom_greeting=companion.custom_greeting,
            greeting=greeting
        ))

    return response_companions
