import cohere
from ..algos.cluster import *
from ..db_funcs.file_storage import * 
from ..db_funcs.chat_history import * 
api_key = os.environ["COHERE_API_KEY"]
co = cohere.Client(api_key)

SAMPLE = [
    {'role': 'USER', 'text': 'What is autism?'},
    {'role': 'CHATBOT', 'text': 'Autism is defined as a developmental disorder characterized by difficulties with social interaction and communication, and by restricted or repetitive patterns of thought and behavior. (Source: document-page1.pdf, Line 5)'},
    {'role': 'USER', 'text': 'What are the symptoms of autism?'},
    {'role': 'CHATBOT', 'text': 'Symptoms of autism include challenges with social interactions, such as understanding and maintaining conversations, restricted interests, repetitive behaviors, and heightened sensitivity to sensory input. (Source: document-page2.pdf, Line 12)'}

]


def chat(prompt, username):
    closest_files = give_closest_cluster(prompt)
    files_content = retrieve_pdfs(closest_files)
    chat_history = retrieve_chat_history(username)
    texts = [extract_text(data) for data in files_content]
    documents = [{'title': closest_files[i], 'snippet': texts[i]} for i in range(len(closest_files))]
    response = co.chat(
        model="command-r-plus",
        message=prompt,
        documents=documents,
        chat_history=SAMPLE + chat_history
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

print(chat("What is autism? Could you explain the key updates and cite the relevant document titles and line numbers in your response?", 'boss'))