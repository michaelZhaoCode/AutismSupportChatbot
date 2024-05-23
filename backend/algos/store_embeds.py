import cohere
import fitz  # PyMuPDF
from ..db_funcs.file_storage import *
from ..db_funcs.embed_storage import *
from io import BytesIO
import numpy as np

api_key = os.environ["COHERE_API_KEY"]
co = cohere.Client(api_key)

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
# print(extract_text(retrieve_all_pdfs()[0][1]))

def calc_embeddings():
    filenames, file_data = retrieve_all_pdfs()
    file_texts = [extract_text(data) for data in file_data]

    embeddings = co.embed(texts=file_texts).embeddings
    data = zip(filenames, embeddings)
    bulk_store_embeddings(data)
    

# calc_embeddings()



