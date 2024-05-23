from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
load_dotenv()
import os 
from ..db_funcs.utils import setup 
from collections import defaultdict

def store_cluster(centroids, embeddings):
    db = setup()

    # Select or create the embeddings collection
    clusters_collection = db['clusters']


    cluster = defaultdict(list)
    for i in range(len(centroids)):
        centroid = centroids[i]
        embedding = embeddings[i]
        cluster[tuple(centroid)].append(embedding)

   
    cluster_documents = [
    {
    'centroid': centroid,
    'embeddings': cluster[centroid]
    } for centroid in cluster
    ]
   
    clusters_collection.insert_many(cluster_documents)
        



def retrieve_cluster():
    db = setup()

    clusters_collection = db['clusters']

    cluster = {tuple(document['centroid']): document['embeddings'] for document in clusters_collection.find()}
    return cluster

def delete_cluster():
    db = setup()
    db.drop_collection('clusters')
# delete_cluster()