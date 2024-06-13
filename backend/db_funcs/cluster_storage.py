"""
cluster_storage.py

This module provides functions to store, retrieve, and delete clustering data in a MongoDB database.
"""
from collections import defaultdict

from utils import setup


def store_cluster(centroids: list[list[float]], embeddings_and_names: list[tuple[str, list[float]]]) -> None:
    """
    Store the centroids and their associated embeddings in the MongoDB database.

    Args:
        centroids (list[list[float]]): A list of centroid coordinates.
        embeddings_and_names (list[tuple[str, list[float]]]): A list of tuples, each containing a name and its
            corresponding embedding.
    """
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


def retrieve_cluster() -> dict[tuple[float, ...], list[tuple[str, list[float]]]]:
    """
    Retrieve the stored clustering data from the MongoDB database.

    Returns:
        dict[tuple[float, ...], list[tuple[str, list[float]]]]: A dictionary where the keys are centroids and the values
            are lists of tuples containing names and embeddings.
    """
    db = setup()

    clusters_collection = db['clusters']

    cluster = {tuple(document['centroid']): document['embedding_and_name'] for document in clusters_collection.find()}
    return cluster


def delete_cluster() -> None:
    """
    Delete the clustering data from the MongoDB database.
    """
    db = setup()
    db.drop_collection('clusters')
# delete_cluster()
