from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
load_dotenv()
import os 
import gridfs

def setup():
    
    uri = f"mongodb+srv://{os.environ['DB_USERNAME']}:{os.environ['DB_PASSWORD']}@cluster0.8qhxlxg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    # Create a new client and connect to the server
    client = MongoClient(uri)

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    return client

def retrieve_pdf(client, pdf_name):
    # Select the database
    db = client['mydatabase']
    
    # Create a GridFS object
    fs = gridfs.GridFS(db)
    
    # Retrieve the file from GridFS
    file_data = fs.find_one({'filename': pdf_name})
    
    if file_data:
        # Read the file data into memory
        pdf_content = file_data.read()
        print(f"Retrieved PDF file '{pdf_name}' successfully.")
        return pdf_content
    else:
        print(f"PDF file '{pdf_name}' not found in the database.")
        return None


def store_pdf(client, pdf_path, pdf_name):
    # Select the database
    db = client['mydatabase']
    
    # Create a GridFS object
    fs = gridfs.GridFS(db)

    # Ensure a unique index on the filename field in the fs.files collection
    db.fs.files.create_index([('filename', 1)], unique=True)
    
    # Open the PDF file and store it in GridFS
    with open(pdf_path, 'rb') as file:
        fs.put(file, filename=pdf_name)
        print(f"Stored PDF file '{pdf_name}' successfully.")


def delete_pdf(client, pdf_name):
    # Select the database
    db = client['mydatabase']
    
    # Create a GridFS object
    fs = gridfs.GridFS(db)
    
    # Find the file in GridFS
    file_data = fs.find_one({'filename': pdf_name})
    
    if file_data:
        # Delete the file using its _id
        fs.delete(file_data._id)
        print(f"Deleted PDF file '{pdf_name}' successfully.")
    else:
        print(f"PDF file '{pdf_name}' not found in the database.")


def empty_database(client):
    # Select the database
    db_name = 'mydatabase'
    db = client[db_name]
    
    # Drop all collections in the database
    for collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
        print(f"Dropped collection: {collection_name}")
    
    print(f"Emptied the database: {db_name}")


client = setup()
# store_pdf(client, '../../Varun_Sahni_Resume.pdf', 'Varun_Sahni_Resume')
delete_pdf(client, 'Varun_Sahni_Resume')
content = retrieve_pdf(client, 'Varun_Sahni_Resume')
# with open('new.pdf', 'wb') as f:
#     f.write(content)

