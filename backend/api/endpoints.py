import cohere
from ..algos.cluster import *
from ..db_funcs.file_storage import * 
api_key = os.environ["COHERE_API_KEY"]
co = cohere.Client(api_key)



def chat(prompt):
    closest_files = give_closest_cluster(prompt)
    files_content = retrieve_pdfs(closest_files)
    texts = [extract_text(data) for data in files_content]
    documents = [{'title': closest_files[i], 'snippet': texts[i]} for i in range(len(closest_files))]
    response = co.chat(
        model="command-r-plus",
        message=prompt,
        documents=documents
        )
    return response.text



def add_pdf(pdf_path, pdf_name):
    store_pdf(pdf_path, pdf_name)
    compute_cluster([pdf_name])

def populate_pdfs(directory_path):
    files_list = [(filename, os.path.join(directory_path, filename)) for filename in os.listdir(directory_path)]
    bulk_insert_pdf(files_list)
    compute_cluster([file_pair[0] for file_pair in files_list])
# populate_pdfs('pdfs')

print(chat("What is autism? Could you explain the key updates and cite the relevant document titles and line numbers in your response?"))