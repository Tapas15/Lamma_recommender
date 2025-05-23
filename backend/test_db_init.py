import asyncio
from utils.database import Database, init_db

async def main():
    # Connect to the database first
    await Database.connect_db()
    
    try:
        # Then initialize collections
        await init_db()
        print("Database initialization complete!")
    except Exception as e:
        print(f"Error during initialization: {e}")
    finally:
        # Close the connection
        await Database.close_db()

if __name__ == "__main__":
    asyncio.run(main()) 