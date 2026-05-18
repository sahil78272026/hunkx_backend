import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL").replace("postgresql+asyncpg://", "postgresql://")

async def run():
    conn = await asyncpg.connect(db_url)
    print("Connected to DB.")
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS user_carts (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
            cart_items JSONB NOT NULL DEFAULT '[]'::jsonb,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    print("Table created.")

    await conn.execute('''
        ALTER TABLE user_carts ENABLE ROW LEVEL SECURITY;
        
        DROP POLICY IF EXISTS "Users can view their own cart" ON user_carts;
        CREATE POLICY "Users can view their own cart" ON user_carts
            FOR SELECT USING (auth.uid() = user_id);
            
        DROP POLICY IF EXISTS "Users can update their own cart" ON user_carts;
        CREATE POLICY "Users can update their own cart" ON user_carts
            FOR UPDATE USING (auth.uid() = user_id);
            
        DROP POLICY IF EXISTS "Users can insert their own cart" ON user_carts;
        CREATE POLICY "Users can insert their own cart" ON user_carts
            FOR INSERT WITH CHECK (auth.uid() = user_id);
    ''')
    print("RLS Policies created.")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(run())
