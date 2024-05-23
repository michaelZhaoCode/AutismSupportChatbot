import numpy as np
from sklearn.cluster import KMeans
from ..db_funcs.embed_storage import *
from ..db_funcs.cluster_storage import *
import cohere


api_key = os.environ["COHERE_API_KEY"]
co = cohere.Client(api_key)
def compute_cluster():
    names, embeddings = retrieve_all_embeddings()

    # Number of clusters
    num_clusters = 6

    # Create KMeans model
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)

    # Fit the model to the embeddings data
    kmeans.fit(embeddings)

    centroids = [kmeans.cluster_centers_[i] for i in kmeans.labels_]
    store_cluster(centroids, list(zip(names, embeddings)))

def give_closest_cluster(text):
    # shouldnt just attach centroid to embedding bc then need to group clusters evey time during inference instead of just once 
    # more intuitive to store clusters as groupings
    # centroid index when using argmin is different from label, labels can be in any order as they correspond to embeddings
    new_embedding = np.array(co.embed(texts=text).embeddings[0])
    
    cluster = retrieve_cluster()
    centroids = np.array(list(cluster.keys()))
    for centroid in centroids:
        for embed in cluster[tuple(centroid)]:
            print(embed[0])


    distances = np.linalg.norm(centroids - new_embedding, axis=1)
    closest_cluster = cluster[tuple(centroids[np.argmin(distances)])]
    return closest_cluster

    
compute_cluster()
print(give_closest_cluster(['I am autistic'])[1][0])