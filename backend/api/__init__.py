from flask import Flask, request, jsonify
import cohere
import os
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
from endpoints import populate_pdfs, add_pdf, chat

load_dotenv("../.env")

api_key = os.environ["COHERE_API_KEY"]
co = cohere.Client(api_key)

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


@app.route('/')
def index():
    return "hello"


@app.route('/chat/', methods=['POST'])
@cross_origin()
def chat():
    username = request.get_json()['username']
    message = request.get_json()['message']
    usertype = request.get_json()['usertype']

    return jsonify({'status': 'success'}), 200


if __name__ == "__main__":
    # populate_pdfs('pdfs')
    print(chat(
        "What is autism? Could you explain the key updates and cite the relevant document titles and line numbers in "
        "your response?",
        'boss'), co)
