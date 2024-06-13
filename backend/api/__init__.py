import cohere
import os
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv

from api.endpoints import populate_pdfs, add_pdf, chat

load_dotenv()

api_key = os.environ["COHERE_API_KEY"]
co = cohere.Client(api_key)

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
            return jsonify({'error': 'Missing required fields'}), 400

        username = data['username']
        message = data['message']
        usertype = data['usertype']

        # Validate usertype
        valid_usertypes = ['child', 'adult', 'researcher']
        if usertype.lower() not in valid_usertypes:
            return jsonify({'error': 'Invalid usertype'}), 400

        # Call the chat function
        response = chat(message, username, usertype, co)

        return jsonify({'response': response}), 200

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({'error': 'An error occurred while processing the request'}), 500


if __name__ == "__main__":
    # print("Populating database")
    # populate_pdfs('../pdfs', co)
    print("Chatting")
    # print(chat(
    #     "What is autism?",
    #     'Michael', usertype="Child", co=co))
