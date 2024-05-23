from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
load_dotenv()
import os 
from ..db_funcs.utils import setup 


def store_embeddings(file_name, embeddings):
    db = setup()

    
    # Select or create the embeddings collection
    embeddings_collection = db['embeddings']

    embeddings_collection.create_index([('file_name', 1)], unique=True)
    
    # Create the embedding document
    embedding_documents = {
        'file_name': file_name,
        'embeddings': embeddings,
    }
    
    # Insert the embedding document into the collection
    embeddings_collection.insert_one(embedding_document)
    print(f"Stored embeddings for file_name {file_name}.")

def bulk_store_embeddings(embeddings_data):
    db = setup()

    
    # Select or create the embeddings collection
    embeddings_collection = db['embeddings']

    embeddings_collection.create_index([('file_name', 1)], unique=True)
    
    # Create the embedding document
    embedding_documents = [
        {
        'file_name': file_name,
        'embeddings': embeddings,
    } for file_name, embeddings in embeddings_data
    ]
    
    # Insert the embedding document into the collection
    embeddings_collection.insert_many(embedding_documents)


def retrieve_embeddings(filename):
    # Select the database
    db = setup()

    embeddings_collection = db['embeddings']

    document = embeddings_collection.find_one({'file_name': filename})

    if document:
        # Read the file data into memory
        embeddings = document['embeddings']
        print(f"Retrieved embeddings successfully.")
        return embeddings
    else:
        print(f"PDF file '{filename}' not found in the database.")
        return None

def retrieve_all_embeddings():

    db = setup()
    embeddings_collection = db['embeddings']
    all_embeddings = []
    names = []
    for document in embeddings_collection.find():
        all_embeddings.append(document['embeddings'])
        names.append(document['file_name'])

    return names, all_embeddings



