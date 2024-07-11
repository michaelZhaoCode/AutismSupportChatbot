"""
utils.py

This module provides utility functions for setting up a MongoDB connection,
manipulating PDF files, and extracting text from PDFs. The main functionalities
include setting up the database, emptying the database, creating smaller PDFs
from a larger one, and extracting text from a PDF content stream.
"""
import os
import fitz
from pymongo.mongo_client import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv
from io import BytesIO


def setup() -> Database:
    """
    Sets up the MongoDB connection using environment variables and returns the database instance.

    Loads the environment variables from a .env file, creates a MongoDB client, and
    attempts to ping the server to ensure a successful connection.

    Returns:
        db (Database): The database client instance connected to the MongoDB server.
    """
    load_dotenv()

    uri = f"mongodb+srv://{os.environ['DB_USERNAME']}:{os.environ['DB_PASSWORD']}{os.environ['DB_LINK']}"

    # Create a new client and connect to the server
    client = MongoClient(uri)

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    db = client['mydatabase']
    return db


def empty_database() -> None:
    """
    Drop all collections in the MongoDB database.
    """
    # Select the database
    db = setup()

    # Drop all collections in the database
    for collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
        print(f"Dropped collection: {collection_name}")

    print(f"Emptied the database")


def create_pdfs(big_pdf_path: str, output_dir: str = 'pdfs') -> None:
    """
    Split a large PDF into smaller PDFs with two pages each.

    Args:
        big_pdf_path (str): The path to the large PDF file.
        output_dir (str): The directory to save the smaller PDFs. Defaults to 'pdfs'.
    """
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the large PDF
    pdf_document = fitz.open(big_pdf_path)

    total_pages = pdf_document.page_count
    for i in range(0, total_pages, 2):
        output_pdf = fitz.open()  # Create a new PDF
        output_pdf.insert_pdf(pdf_document, from_page=i, to_page=min(i + 1, total_pages - 1))

        output_pdf_path = os.path.join(output_dir, f"document-page{i // 2 + 1}.pdf")
        output_pdf.save(output_pdf_path)
        output_pdf.close()

        print(f"Created {output_pdf_path}")

    pdf_document.close()


def extract_text(pdf_content: bytes) -> str:
    """
    Extract text from a PDF file.

    Args:
        pdf_content (bytes): The content of the PDF file in bytes.

    Returns:
        str: The extracted text from the PDF.
    """
    pdf_stream = BytesIO(pdf_content)

    # Open the PDF file
    document = fitz.open(stream=pdf_stream, filetype="pdf")

    # Initialize an empty string to store the extracted text
    text = ""

    # Iterate over each page in the PDF
    for page_num in range(len(document)):
        page = document.load_page(page_num)  # Load a page
        text += page.get_text()  # Extract text from the page

    # Close the document
    document.close()

    return text


if __name__ == "__main__":
    # create_pdfs('autism_handbook.pdf')
    empty_database()
    pass
