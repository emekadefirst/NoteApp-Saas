from src.configs.env import DB_URI
from pymongo import AsyncMongoClient


client = AsyncMongoClient(
    DB_URI,
    minPoolSize=5,
    maxPoolSize=50,
    maxIdleTimeMS=600_000,
    serverSelectionTimeoutMS=5000,
    socketTimeoutMS=10000,
    connectTimeoutMS=5000,
    retryWrites=True,
)


async def get_collection(collection_name: str):
    db = client["notesas"] 
    return db[collection_name]  
