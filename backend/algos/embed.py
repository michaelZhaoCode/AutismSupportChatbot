from ..db_funcs.file_storage import *
from ..db_funcs.cluster_storage import *
from ..utils import *
import cohere

api_key = os.environ["COHERE_API_KEY"]
co = cohere.Client(api_key)

# when user calls insert or bulk insert, we dont need to directly call insert/bulk insert and thats it
# whatever new files are being added, pass those in when re-computing cluster
# for eg. for first bulkinsert, retireve cluster (it will be empty) and then use all of its embeddings + newly computed embeddings for new files
# this is same process for adding to embeddings table, u still need to know when to add embeddings
# this way it is nicely synced, whenever adding files, cluster also recomputed with new files embeddigns calculated

def retrieve_all_embeddings(new_files=[], is_insert=True):

    cluster = retrieve_cluster()

    names = []
    embeddings = []
    for centroid in cluster:
        for name, embedding in cluster[centroid]:
            names.append(name)
            embeddings.append(embedding)
    if is_insert:
        new_embeddings = calc_embeddings(new_files)
        names.extend(new_files)
        embeddings.extend(new_embeddings)
    else:
        files_set = set(new_files)
        new_names = []
        new_embeddings = []
        for name in names:
            if name not in files_set:
                new_names.append(name)
                new_embeddings.append(calc_embeddings([name])[0])
    return names, embeddings 

def calc_embeddings(file_names):
    file_content = retrieve_pdfs(file_names)
    file_texts = [extract_text(content) for content in file_content]
    embeddings = co.embed(texts=file_texts).embeddings
    return embeddings
