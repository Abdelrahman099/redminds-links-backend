import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv() # take environment variables from .env.

MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb://localhost:27017") # Default to localhost if not set

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.link_db # Database name: link_db

link_collection = database.get_collection("links") # Collection name: links

# Helper function to parse MongoDB results
def link_helper(link) -> dict:
    # Ensure the _id is properly converted to string
    return {
        "id": str(link["_id"]),
        "url": link["url"],
        "name": link["name"]
    }

