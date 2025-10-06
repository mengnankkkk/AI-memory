import hashlib
import json
from app.core.redis_client import get_redis

async def get_llm_cache_key(user_id: str, companion_id: int, prompt: str, context: list) -> str:
    key_raw = f"llm:{user_id}:{companion_id}:{prompt}:{json.dumps(context, ensure_ascii=False)}"
    return hashlib.sha256(key_raw.encode('utf-8')).hexdigest()

async def get_cached_llm_response(cache_key: str):
    redis = await get_redis()
    return await redis.get(f"llmresp:{cache_key}")

async def set_cached_llm_response(cache_key: str, response: str, expire: int = 300):
    redis = await get_redis()
    await redis.set(f"llmresp:{cache_key}", response, ex=expire)
