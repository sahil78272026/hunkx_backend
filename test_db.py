import asyncio
# pyrefly: ignore [missing-import]
import asyncpg

async def main():
    dsn = "postgresql://postgres.rlrcugmcgkbuhridzryj:Onemennavy%401234@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"
    print("Testing connection to pooler...")
    try:
        conn = await asyncpg.connect(dsn)
        print("Success! Connected to DB.")
        await conn.execute("SELECT 1")
        await conn.close()
    except Exception as e:
        print(f"Failed: {e}")

asyncio.run(main())
