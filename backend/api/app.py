import os
import logging
import threading
from openai import OpenAI
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv

from api.chatbot import Chatbot
from api.botservice.gpt_botservice import GPTBotService
from api.servicehandler.botservice_servicehandler import BotserviceServiceHandler
from api.locationdatabase.sqlitelocationdatabase import SQLiteLocationDatabase

from db_funcs.unified_pinecone_storage import UnifiedPineconeStorage
from db_funcs.chat_history import ChatHistoryInterface
from utils import setup_mongo_db
from logger import setup_logger

load_dotenv()

# Running this setup in main.py will not correctly initialise settings, so the logger must be set up in here
# NOTE: currently, the logger will always log to the file app.log even through multiple running processes
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

chat_history = ChatHistoryInterface(mongo_db)

# Initialize unified Pinecone storage for PDFs and embeddings
storage = UnifiedPineconeStorage()
logger.info("Connected to Pinecone storage")

service_handler = BotserviceServiceHandler(botservice, location_database)

chatbot_obj = Chatbot(storage, chat_history, botservice, service_handler)
logger.info("Initialised all global app instances")

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


@app.route('/')
def index():
    return "hello"


@app.route('/generate/', methods=['POST'])
@cross_origin()
def generate():
    try:
        data = request.get_json()

        # Validate required keys
        if not all(key in data for key in ('username', 'message', 'usertype')):
            logger.warning("/generate/: Request missing a required field")
            return jsonify({'error': 'Missing required fields'}), 400

        username = data.get('username')
        message = data.get('message')
        usertype = data.get('usertype')
        location = data.get('location', "")
        region_id = data.get('region_id', -1)

        # Validate usertype
        if usertype.lower() not in {'child', 'adult', 'researcher'}:
            logger.warning("/generate/: Request has invalid usertype %s", usertype.lower())
            return jsonify({'error': 'Invalid usertype'}), 400

        # Validate and cast region_id to int
        if region_id:
            try:
                region_id = int(region_id)  # Attempt to cast to int
            except ValueError:
                return jsonify({'error': 'region_id must be an integer'}), 400

        # Call the chat function
        response = chatbot_obj.chat(message, username, usertype, location, region_id)

        threading.Thread(target=chatbot_obj.update_user, args=(username, message, response["response"])).start()

        return jsonify(response), 200

    except Exception as e:
        logger.error("/generate/: %s", e)
        return jsonify({'error': 'An error occurred while processing the request'}), 500


@app.route('/retrieve_regions', methods=['GET'])
@cross_origin()
def retrieve_regions():
    try:
        results = location_database.load_snapshot()
        return jsonify({'response': results}), 200

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({'error': 'An error occurred while retrieving regions'}), 500


@app.route('/storage_stats', methods=['GET'])
@cross_origin()
def storage_stats():
    """Get statistics about the PDF storage."""
    try:
        stats = chatbot_obj.get_storage_stats()
        return jsonify({'response': stats}), 200
    except Exception as e:
        logger.error("/storage_stats/: %s", e)
        return jsonify({'error': 'An error occurred while retrieving storage stats'}), 500


if __name__ == "__main__":
    # print("Populating database")
    # chatbot_obj.populate_pdfs('../pdfs')
    # chatbot_obj.add_pdf("../pdfs/autism_handbook.pdf")
    # print("Chatting")
    # print(chatbot_obj.chat("Hello", "Bob", "Adult"))
    # print("Cleared")
    # chatbot_obj.clear_history("Michael")
    pass
