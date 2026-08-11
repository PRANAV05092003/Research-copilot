import asyncio
import sys

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine


async def verify():
    print("Verifying PostgreSQL connectivity...")
    try:
        engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/copilot")
        async with engine.connect() as conn:
            print("PostgreSQL connection successful.")
            # Verify pgvector
            try:
                await conn.execute(engine.dialect.statement_compiler.statement_cls("CREATE EXTENSION IF NOT EXISTS vector"))
                print("pgvector extension is available.")
            except Exception as e:
                print(f"Error checking pgvector: {e}")
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        sys.exit(1)

    print("Verifying Redis connectivity...")
    try:
        redis = Redis.from_url("redis://localhost:6379/0")
        await redis.ping()
        print("Redis connection successful.")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(verify())
