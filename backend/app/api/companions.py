"""
角色(Companion)管理API - 支持用户认证
"""
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict
from app.core.database import get_db
from app.models.companion import Companion
from app.models.user import User
from app.api.schemas import CompanionCreate, CompanionResponse
from app.api.schemas_auth import CompanionCreate as AuthCompanionCreate, CompanionResponse as AuthCompanionResponse
from app.api.dependencies import get_current_active_user
from app.core.prompts import get_greeting
from app.core.redis_client import get_redis
import logging

logger = logging.getLogger("companions_api")

router = APIRouter(prefix="/companions", tags=["companions"])


@router.get("/system", response_model=List[AuthCompanionResponse])
async def get_system_companions(
    db: AsyncSession = Depends(get_db)
):
    """
    获取系统预设的AI伙伴列表

    无需认证，所有用户都可以查看
    """
    result = await db.execute(
        select(Companion).where(Companion.user_id == 1)
        .order_by(Companion.id)
    )
    companions = result.scalars().all()

    logger.info(f"获取系统预设角色列表，共 {len(companions)} 个")

    return [
        AuthCompanionResponse(
            id=c.id,
            user_id=str(c.user_id),  # 转换为字符串
            name=c.name,
            avatar_id=c.avatar_id,
            personality_archetype=c.personality_archetype,
            custom_greeting=c.custom_greeting,
            description=getattr(c, 'description', ''),
            created_at=c.created_at
        )
        for c in companions
    ]


@router.get("/", response_model=List[AuthCompanionResponse])
async def get_user_companions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的所有角色

    需要认证
    """
    result = await db.execute(
        select(Companion).where(Companion.user_id == current_user.id)
        .order_by(Companion.created_at.desc())
    )
    companions = result.scalars().all()

    logger.info(f"用户 {current_user.username} 获取角色列表，共 {len(companions)} 个")

    return [
        AuthCompanionResponse(
            id=c.id,
            user_id=str(current_user.id),  # 转换为字符串
            name=c.name,
            avatar_id=c.avatar_id,
            personality_archetype=c.personality_archetype,
            custom_greeting=c.custom_greeting,
            description=getattr(c, 'description', ''),
            created_at=c.created_at
        )
        for c in companions
    ]


@router.post("/", response_model=AuthCompanionResponse)
async def create_companion(
    companion_data: AuthCompanionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新角色

    需要认证
    """
    # 检查用户是否已有同名角色
    result = await db.execute(
        select(Companion).where(
            Companion.user_id == current_user.id,
            Companion.name == companion_data.name
        )
    )
    existing_companion = result.scalar_one_or_none()

    if existing_companion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已经创建了同名的角色"
        )

    # 创建新角色
    new_companion = Companion(
        user_id=current_user.id,
        name=companion_data.name,
        avatar_id=companion_data.avatar_id,
        personality_archetype=companion_data.personality_archetype,
        custom_greeting=companion_data.custom_greeting
    )

    db.add(new_companion)
    await db.commit()
    await db.refresh(new_companion)

    logger.info(
        f"用户 {current_user.username} 创建新角色: {new_companion.name} "
        f"(ID: {new_companion.id})"
    )

    return AuthCompanionResponse(
        id=new_companion.id,
        user_id=str(current_user.id),  # 转换为字符串
        name=new_companion.name,
        avatar_id=new_companion.avatar_id,
        personality_archetype=new_companion.personality_archetype,
        custom_greeting=new_companion.custom_greeting,
        created_at=new_companion.created_at
    )


@router.get("/{companion_id}", response_model=CompanionResponse)
async def get_companion(
    companion_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个角色信息

    需要认证，且只能获取自己的角色
    """
    # 先检查Redis缓存
    redis = await get_redis()
    cache_key = f"companion:{companion_id}:user:{current_user.id}"
    cached = await redis.get(cache_key)

    if cached:
        import json
        return CompanionResponse(**json.loads(cached))

    # 从数据库获取
    # 首先尝试获取用户自己的伙伴
    result = await db.execute(
        select(Companion).where(
            Companion.id == companion_id,
            Companion.user_id == current_user.id
        )
    )
    companion = result.scalar_one_or_none()
    
    # 如果没找到，尝试获取系统预设伙伴（user_id=1）
    if not companion:
        result = await db.execute(
            select(Companion).where(
                Companion.id == companion_id,
                Companion.user_id == 1  # 系统预设伙伴
            )
        )
        companion = result.scalar_one_or_none()

    if not companion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在或无权访问"
        )

    greeting = get_greeting(companion.name, companion.personality_archetype)

    resp = CompanionResponse(
        id=companion.id,
        user_id=str(companion.user_id),  # 转换为字符串
        name=companion.name,
        avatar_id=companion.avatar_id,
        personality_archetype=companion.personality_archetype,
        custom_greeting=companion.custom_greeting,
        description=getattr(companion, 'description', ''),
        greeting=greeting,
        prompt_version=getattr(companion, 'prompt_version', 'v1')
    )

    # 缓存10分钟
    await redis.set(cache_key, resp.model_dump_json(), ex=600)

    return resp


@router.delete("/{companion_id}")
async def delete_companion(
    companion_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除角色

    需要认证，且只能删除自己的角色
    """
    result = await db.execute(
        select(Companion).where(
            Companion.id == companion_id,
            Companion.user_id == current_user.id
        )
    )
    companion = result.scalar_one_or_none()

    if not companion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在或无权访问"
        )

    await db.delete(companion)
    await db.commit()

    # 清理缓存
    redis = await get_redis()
    await redis.delete(f"companion:{companion_id}:user:{current_user.id}")

    logger.info(f"用户 {current_user.username} 删除角色: {companion.name}")

    return {"message": "角色删除成功"}


@router.put("/{companion_id}", response_model=CompanionResponse)
async def update_companion(
    companion_id: int,
    data: Dict = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新伙伴信息

    需要认证
    """
    result = await db.execute(
        select(Companion).where(
            Companion.id == companion_id,
            Companion.user_id == current_user.id
        )
    )
    companion = result.scalar_one_or_none()

    if not companion:
        raise HTTPException(status_code=404, detail="伙伴不存在或无权访问")

    # 更新字段
    for key, value in data.items():
        if hasattr(companion, key):
            setattr(companion, key, value)

    # 默认prompt_version
    if not hasattr(companion, 'prompt_version'):
        setattr(companion, 'prompt_version', data.get('prompt_version', 'v1'))

    await db.commit()
    await db.refresh(companion)

    # 清理缓存
    redis = await get_redis()
    await redis.delete(f"companion:{companion_id}:user:{current_user.id}")

    greeting = get_greeting(companion.name, companion.personality_archetype)

    logger.info(f"用户 {current_user.username} 更新角色: {companion.name}")

    return CompanionResponse(
        id=companion.id,
        user_id=companion.user_id,
        name=companion.name,
        avatar_id=companion.avatar_id,
        personality_archetype=companion.personality_archetype,
        custom_greeting=companion.custom_greeting,
        greeting=greeting,
        prompt_version=getattr(companion, 'prompt_version', 'v1')
    )


@router.post("/{companion_id}/reset")
async def reset_companion(
    companion_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    重置伙伴为默认配置

    需要认证
    """
    result = await db.execute(
        select(Companion).where(
            Companion.id == companion_id,
            Companion.user_id == current_user.id
        )
    )
    companion = result.scalar_one_or_none()

    if not companion:
        raise HTTPException(status_code=404, detail="伙伴不存在或无权访问")

    companion.personality_archetype = "listener"
    companion.custom_greeting = None

    if hasattr(companion, 'prompt_version'):
        companion.prompt_version = 'v1'

    await db.commit()
    await db.refresh(companion)

    # 清理缓存
    redis = await get_redis()
    await redis.delete(f"companion:{companion_id}:user:{current_user.id}")

    logger.info(f"用户 {current_user.username} 重置角色: {companion.name}")

    return {"message": "伙伴已重置为默认配置"}
