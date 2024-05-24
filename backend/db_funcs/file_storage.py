from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
load_dotenv()
import os 
import gridfs
from ..utils import * 

def retrieve_pdfs(pdf_names):
    # Select the database
    db = setup()
    
    # Create a GridFS object
    fs = gridfs.GridFS(db)
    data = []
    for pdf_name in pdf_names:
    
        # Retrieve the file from GridFS
        file_data = fs.find_one({'filename': pdf_name})
        
        if file_data:
            # Read the file data into memory
            pdf_content = file_data.read()
            print(f"Retrieved PDF file '{pdf_name}' successfully.")
            data.append(pdf_content)
        else:
            print(f"PDF file '{pdf_name}' not found in the database.")
            return None
    return data


def store_pdf(pdf_path, pdf_name):
    db = setup()

    
    # Create a GridFS object
    fs = gridfs.GridFS(db)

    # Ensure a unique index on the filename field in the fs.files collection
    db.fs.files.create_index([('filename', 1)], unique=True)
    
    # Open the PDF file and store it in GridFS
    with open(pdf_path, 'rb') as file:
        fs.put(file, filename=pdf_name)
        print(f"Stored PDF file '{pdf_name}' successfully.")

def bulk_insert_pdf(files_list):
    db = setup()
    
    # Create a GridFS object
    fs = gridfs.GridFS(db)

    # Ensure a unique index on the filename field in the fs.files collection
    db.fs.files.create_index([('filename', 1)], unique=True)
    for name, path in files_list:
        # Open the PDF file and store it in GridFS
        with open(path, 'rb') as file:
            fs.put(file, filename=name)
            print(f"Stored PDF file '{name}' successfully.")

def delete_pdf(pdf_name):
    db = setup()

    
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

def retrieve_all_pdfs():
    db = setup()

    # Create a GridFS object
    fs = gridfs.GridFS(db)
    

    filenames = []
    file_data = []
    # Find all files in the fs.files collection
    for grid_out in fs.find():
        filename = grid_out.filename
        filenames.append(filename)
        file_data.append(grid_out.read())
    return filenames, file_data

    





# store_pdf('autism_handbook.pdf', 'autism_handbook')


# # store_pdf(client, '../../Varun_Sahni_Resume.pdf', 'Varun_Sahni_Resume')
# delete_pdf(client, 'Varun_Sahni_Resume')
# content = retrieve_pdf(client, 'Varun_Sahni_Resume')
# # with open('new.pdf', 'wb') as f:
# #     f.write(content)

