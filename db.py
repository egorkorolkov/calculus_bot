import os
import datetime
import pytz
from motor.motor_asyncio import AsyncIOMotorClient
from utils import return_on_failure, ERROR_CODES
from logger import app_logger
from dotenv import load_dotenv


load_dotenv()


MONGO_URI = os.getenv('MONGO_DB_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')


class MongoDBHandler:
    @return_on_failure(ERROR_CODES.DB_ERROR.value, app_logger)
    def __init__(self):
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        self.chat_collection = db['chat_history']

    @return_on_failure(ERROR_CODES.DB_ERROR.value, app_logger)
    async def get_user_history(self, user_id: int) -> list:
        user_chat = await self.chat_collection.find_one({'user_id': user_id})
        if user_chat:
            return user_chat['history']
        else:
            return []
        
    @return_on_failure(ERROR_CODES.DB_ERROR.value, app_logger)
    async def update_user_history(self, user_id, role, content):
        return await self.chat_collection.update_one(
            {'user_id': user_id},
            {'$push': {'history': {'role': role, 'content': content}}},
            upsert=True
        )

    @return_on_failure(ERROR_CODES.DB_ERROR.value, app_logger)
    async def add_new_user(self, user_id, system_prompt):
        user_chat = await self.chat_collection.find_one({'user_id': user_id})
        if not user_chat:
            return await self.chat_collection.insert_one({
                'user_id': user_id,
                'history': [{'role': 'system', 'content': system_prompt}]
            })

    @return_on_failure(ERROR_CODES.DB_ERROR.value, app_logger)
    async def clear_user_history(self, user_id):
        user_chat = await self.chat_collection.find_one({'user_id': user_id})
        if user_chat:
            return await self.chat_collection.update_one(
                {'user_id': user_id},
                {'$set': {'history': []}}
            )