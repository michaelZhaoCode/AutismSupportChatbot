import cohere
from ..algos.cluster import *
from ..algos.store_embeds import *

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


print(chat("What is autism?"))

