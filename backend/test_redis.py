import asyncio
from app.core.redis_client import get_redis

async def test_redis():
    try:
        redis = await get_redis()
        result = await redis.ping()
        print(f'Redis连接状态: {result}')
        return True
    except Exception as e:
        print(f'Redis连接失败: {e}')
        return False

if __name__ == "__main__":
    asyncio.run(test_redis())
