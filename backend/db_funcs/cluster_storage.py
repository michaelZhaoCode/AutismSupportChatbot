from dotenv import load_dotenv
load_dotenv()
import os 
from ..utils import *
from collections import defaultdict

def store_cluster(centroids, embeddings_and_names):
    db = setup()

    # Select or create the embeddings collection
    clusters_collection = db['clusters']


    cluster = defaultdict(list)
    for i in range(len(centroids)):
        centroid = centroids[i]
        embedding_and_name = embeddings_and_names[i]
        cluster[tuple(centroid)].append(embedding_and_name)

    # each embedding is tuple of (name, embedding val)
    cluster_documents = [
    {
    'centroid': centroid,
    'embedding_and_name': cluster[centroid]
    } for centroid in cluster
    ]
   
    clusters_collection.insert_many(cluster_documents)


def retrieve_cluster():
    db = setup()

    clusters_collection = db['clusters']

    cluster = {tuple(document['centroid']): document['embedding_and_name'] for document in clusters_collection.find()}
    return cluster

def delete_cluster():
    db = setup()
    db.drop_collection('clusters')
# delete_cluster()