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
import logging


logger = logging.getLogger(__name__)


def setup_mongo_db() -> Database:
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
        logger.info("setup_mongo_db: Successfully connected to MongoDB")
    except Exception as e:
        logger.error("setup_mongo_db: %s", e)
    db = client['mydatabase']
    return db


def empty_database() -> None:
    """
    Drop all collections in the MongoDB database.
    """
    # Select the database
    db = setup_mongo_db()

    # Drop all collections in the database
    for collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
        logger.info("empty_database: Dropped collection %s", collection_name)

    logger.info("empty_database: Emptied the database")


def chunk_pdf_in_memory(pdf_path: str) -> list[tuple[str, bytes]]:
    """
    Chunk a PDF into individual pages in memory.

    Args:
        pdf_path (str): Path to the PDF file to chunk.

    Returns:
        list: A list of tuples containing chunk names and their byte content.
    """
    pdf_document = fitz.open(pdf_path)
    big_pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    chunks = []
    total_pages = pdf_document.page_count

    logger.info("chunk_pdf_in_memory: Beginning pdf chunking on file %s with %s pages",
                pdf_path,
                total_pages)
    for i in range(total_pages):
        page = pdf_document.load_page(i)
        if not page.get_text():
            logger.info("chunk_pdf_in_memory: Skipping empty page %s", i + 1)
            continue

        output_pdf = fitz.open()  # Create a new PDF
        output_pdf.insert_pdf(pdf_document, from_page=i, to_page=i)

        pdf_chunk = output_pdf.write()
        chunk_name = f"{big_pdf_name}-page{i + 1}.pdf"
        chunks.append((chunk_name, pdf_chunk))

    pdf_document.close()
    logger.info("chunk_pdf_in_memory: Completed pdf chunking")
    return chunks


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
