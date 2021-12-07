import motor.motor_asyncio

from app.core.env import CREDENTIALS

client = motor.motor_asyncio.AsyncIOMotorClient(CREDENTIALS.MONGODB_URL)
db = client[CREDENTIALS.MONGODB_DBNAME]
