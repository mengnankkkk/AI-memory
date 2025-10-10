import sys
from pathlib import Path

import pytest
from sqlalchemy import delete, select

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.services.affinity_engine import affinity_engine, EmotionAnalysis
from app.services.redis_utils import redis_affinity_manager, redis_stats_manager
from app.core.database import async_session_maker, init_db
from app.models.relationship import (
    CompanionRelationshipState,
    EmotionLog,
    RelationshipHistory,
)
from app.config.affinity_levels import get_level_by_score


@pytest.mark.asyncio
async def test_affinity_engine_persists_relationship_state(monkeypatch):
    user_id = "test-affinity-db"
    companion_id = 98765

    previous_affinity = 90
    affinity_change = 40
    new_affinity = previous_affinity + affinity_change

    previous_trust = 45
    trust_change = 4
    new_trust = previous_trust + trust_change

    previous_tension = 10
    tension_change = -3
    new_tension = previous_tension + tension_change

    new_level = get_level_by_score(new_affinity)

    state = {
        "affinity_score": previous_affinity,
        "trust_score": previous_trust,
        "tension_score": previous_tension,
        "romance_level": "stranger",
        "current_mood": "neutral",
        "total_interactions": 5,
        "memories": []
    }

    async def fake_update_affinity(user, companion, aff_delta, trust_delta, tension_delta, interaction_type="chat"):
        state["affinity_score"] = max(0, min(1000, state["affinity_score"] + aff_delta))
        state["trust_score"] = max(0, min(100, state["trust_score"] + trust_delta))
        state["tension_score"] = max(0, min(100, state["tension_score"] + tension_delta))
        state["romance_level"] = get_level_by_score(state["affinity_score"])
        state["current_mood"] = "test_mood"
        state["total_interactions"] += 1
        return True

    async def fake_get_state(user, companion):
        return state.copy()

    async def fake_add_memory(*args, **kwargs):
        return True

    async def fake_increment_counter(*args, **kwargs):
        return None

    monkeypatch.setattr(redis_affinity_manager, "update_affinity", fake_update_affinity)
    monkeypatch.setattr(redis_affinity_manager, "get_companion_state", fake_get_state)
    monkeypatch.setattr(redis_affinity_manager, "add_memory", fake_add_memory)
    monkeypatch.setattr(redis_stats_manager, "increment_counter", fake_increment_counter)

    await init_db()

    async with async_session_maker() as session:
        await session.execute(delete(EmotionLog).where(EmotionLog.user_id == user_id))
        await session.execute(delete(RelationshipHistory).where(RelationshipHistory.user_id == user_id))
        await session.execute(delete(CompanionRelationshipState).where(CompanionRelationshipState.user_id == user_id))
        await session.commit()

    emotion_analysis = EmotionAnalysis(
        primary_emotion="positive",
        emotion_intensity=0.82,
        detected_emotions=["joy"],
        user_intent="compliment",
        is_appropriate=True,
        violation_reason="",
        suggested_affinity_change=affinity_change,
        suggested_trust_change=trust_change,
        suggested_tension_change=tension_change,
        key_points=["友好互动"],
        is_memorable=False
    )

    await affinity_engine._update_database_automatically(
        user_id=user_id,
        companion_id=companion_id,
        emotion_analysis=emotion_analysis,
        affinity_change=affinity_change,
        trust_change=trust_change,
        tension_change=tension_change,
        new_affinity_score=new_affinity,
        new_trust_score=new_trust,
        new_tension_score=new_tension,
        new_level=new_level,
        level_changed=True,
        user_message="谢谢你的关心！",
        previous_affinity_score=previous_affinity,
        previous_trust_score=previous_trust,
        previous_tension_score=previous_tension,
        previous_level="stranger"
    )

    async with async_session_maker() as session:
        state_stmt = select(CompanionRelationshipState).where(
            CompanionRelationshipState.user_id == user_id,
            CompanionRelationshipState.companion_id == str(companion_id)
        )
        state_result = await session.execute(state_stmt)
        db_state = state_result.scalar_one()

        assert db_state.affinity_score == new_affinity
        assert db_state.trust_score == new_trust
        assert db_state.tension_score == new_tension
        assert db_state.romance_stage == new_level
        flags = db_state.special_flags or {}
        assert flags.get("last_primary_emotion") == emotion_analysis.primary_emotion

        log_stmt = select(EmotionLog).where(
            EmotionLog.user_id == user_id,
            EmotionLog.companion_id == str(companion_id)
        )
        log_result = await session.execute(log_stmt)
        emotion_logs = log_result.scalars().all()
        assert emotion_logs, "emotion log should be persisted"
        assert any(log.primary_emotion == emotion_analysis.primary_emotion for log in emotion_logs)

        history_stmt = select(RelationshipHistory).where(
            RelationshipHistory.user_id == user_id,
            RelationshipHistory.companion_id == str(companion_id)
        )
        history_result = await session.execute(history_stmt)
        history_entries = history_result.scalars().all()
        change_types = {entry.change_type for entry in history_entries}

        assert "level_change" in change_types
        assert "affinity_change" in change_types
