from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect(cls):
        """Kết nối MongoDB"""
        cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
        print(f" Connected to MongoDB: {settings.DATABASE_NAME}")
    
    @classmethod
    async def close(cls):
        """Đóng kết nối MongoDB"""
        if cls.client:
            cls.client.close()
            print(" MongoDB connection closed")
    
    @classmethod
    def get_database(cls):
        """Lấy database instance"""
        return cls.client[settings.DATABASE_NAME]
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """Lấy collection"""
        db = cls.get_database()
        return db[collection_name]

# Shortcut functions
async def get_database():
    return MongoDB.get_database()

def get_collection(name: str):
    return MongoDB.get_collection(name)