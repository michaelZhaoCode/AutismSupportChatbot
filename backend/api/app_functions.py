import os
import logging
import threading
from openai import OpenAI
from flask import jsonify
from dotenv import load_dotenv

from api.chatbot import Chatbot
from api.botservice.gpt_botservice import GPTBotService
from api.servicehandler.botservice_servicehandler import BotserviceServiceHandler
from api.locationdatabase.sqlitelocationdatabase import SQLiteLocationDatabase
from db_funcs.unified_pinecone_storage import UnifiedPineconeStorage
from db_funcs.mongodb_chat_history_data_provider import MongoDBChatHistoryProvider
from utils import setup_mongo_db
from logger import setup_logger

# Initialize all the components needed for the functions
load_dotenv()

setup_logger("app.log")
logger = logging.getLogger(__name__)

api_key = os.environ["OPENAI_API_KEY"]
openai_client = OpenAI(api_key=api_key)
logger.info("Connected to OpenAI")
botservice = GPTBotService(openai_client)

location_database = SQLiteLocationDatabase()
location_database.initialize_database()
location_database.create_snapshot()

# MongoDB is still used for chat history
mongo_db = setup_mongo_db()
chat_history = MongoDBChatHistoryProvider(mongo_db)

# Initialize unified Pinecone storage for PDFs and embeddings
storage = UnifiedPineconeStorage()
logger.info("Connected to Pinecone storage")

service_handler = BotserviceServiceHandler(botservice, location_database)

chatbot_obj = Chatbot(storage, chat_history, botservice, service_handler)
logger.info("Initialised all global app instances")


def index():
    return "hello"


def generate(username, message, usertype, location="", region_id=-1):
    try:
        # Validate usertype
        if usertype.lower() not in {'child', 'adult', 'researcher'}:
            logger.warning("generate(): Invalid usertype %s", usertype.lower())
            return {'error': 'Invalid usertype'}, 400

        # Validate and cast region_id to int
        if region_id:
            try:
                region_id = int(region_id)  # Attempt to cast to int
            except ValueError:
                return {'error': 'region_id must be an integer'}, 400

        # Call the chat function
        response = chatbot_obj.chat(message, username, usertype, location, region_id)

        threading.Thread(target=chatbot_obj.update_user, args=(username, message, response)).start()

        return {'response': response}, 200

    except Exception as e:
        logger.error("generate(): %s", e)
        return {'error': 'An error occurred while processing the request'}, 500


def retrieve_regions():
    try:
        results = location_database.load_snapshot()
        return {'response': results}, 200

    except Exception as e:
        print(f"Error occurred: {e}")
        return {'error': 'An error occurred while retrieving regions'}, 500


def storage_stats():
    """Get statistics about the PDF storage."""
    try:
        stats = chatbot_obj.get_storage_stats()
        return {'response': stats}, 200
    except Exception as e:
        logger.error("storage_stats(): %s", e)
        return {'error': 'An error occurred while retrieving storage stats'}, 500


# Example usage
if __name__ == "__main__":
    # Test the functions
    print(index())
    
    # Test generate function
    response, status_code = generate(
        username="test_user",
        message="Hello, I need information about autism resources",
        usertype="adult"
    )
    print(f"Generate response (status {status_code}):", response)
    
    # Test retrieve_regions function
    regions, status_code = retrieve_regions()
    print(f"Regions (status {status_code}):", regions)
    
    # Test storage_stats function
    stats, status_code = storage_stats()
    print(f"Storage stats (status {status_code}):", stats) 