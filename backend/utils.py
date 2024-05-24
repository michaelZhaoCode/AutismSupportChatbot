from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
load_dotenv()
import os 
import gridfs
from PyPDF2 import PdfWriter, PdfReader
import fitz 
from io import BytesIO



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
    db = client['mydatabase']
    return db



def empty_database():
    # Select the database
    db = setup()
    
    # Drop all collections in the database
    for collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
        print(f"Dropped collection: {collection_name}")
    
    print(f"Emptied the database")


def create_pdfs(big_pdf_path, output_dir='pdfs'):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the large PDF
    pdf_document = fitz.open(big_pdf_path)

    total_pages = pdf_document.page_count
    for i in range(0, total_pages, 2):
        output_pdf = fitz.open()  # Create a new PDF
        output_pdf.insert_pdf(pdf_document, from_page=i, to_page=min(i+1, total_pages-1))

        output_pdf_path = os.path.join(output_dir, f"document-page{i//2 + 1}.pdf")
        output_pdf.save(output_pdf_path)
        output_pdf.close()

        print(f"Created {output_pdf_path}")

    pdf_document.close()

def extract_text(pdf_content):

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



# create_pdfs('autism_handbook.pdf')
# empty_database()