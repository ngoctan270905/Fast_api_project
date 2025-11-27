import redis.asyncio as redis
from app.core.config import settings

# tạo 1 connection pool để tái sử dụng
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True # sẽ chuyển đổi từ bytes sang str
)

# hàm dependency connection để lấy redis client
# async def get_redis_client() -> redis.Redis:
#     return redis.Redis(connection_pool=redis_pool)

# hàm dependency connection để
# lấy redis client -> server thao tác redis -> trả kết quả về enpoin
async def get_redis_client():
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.close()
