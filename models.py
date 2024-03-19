from config import POSTGRES_URI
import asyncpg

async def db_start():
    global conn

    conn = await asyncpg.connect(POSTGRES_URI)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            age INTEGER,
            latitude FLOAT,
            longitude FLOAT,
            bio TEXT,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


async def create_profile(user_id, age, latitude, longitude, bio):
    user = await conn.fetchrow("SELECT 1 FROM users WHERE user_id = $1", user_id)
    if not user:
        await conn.execute(
            """
            INSERT INTO users (user_id, age, latitude, longitude, bio)
            VALUES ($1, $2, $3, $4, $5)
            """,
            user_id, age, latitude, longitude, bio
        )