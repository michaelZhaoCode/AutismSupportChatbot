"""
cluster.py

This module provides functions to compute clusters for embeddings and to find the closest cluster for a given text.
"""
import numpy as np
from sklearn.cluster import KMeans
from math import sqrt

from api.botservice import BotService
from algos.embed import retrieve_all_embeddings
from db_funcs.cluster_storage import ClusterStorageInterface
from db_funcs.file_storage import PDFStorageInterface


def compute_cluster(files_list: list[str], botservice: BotService, cluster_storage: ClusterStorageInterface,
                    pdf_storage: PDFStorageInterface) -> None:
    """
    Compute clusters for the given list of files and store them in the MongoDB database.

    Args:
        files_list (list[str]): List of file names to compute clusters for.
        botservice (BotService): BotService instance for generating embeddings.
    """
    names, embeddings = retrieve_all_embeddings(botservice, new_files=files_list, cluster_storage=cluster_storage,
                                                pdf_storage=pdf_storage)
    cluster_storage.delete_cluster()

    # Number of clusters
    # set to the square root of files in the database
    num_clusters = round(sqrt(len(names)))

    # Create KMeans model
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)

    # Fit the model to the embeddings data
    kmeans.fit(embeddings)

    centroids = [kmeans.cluster_centers_[i] for i in kmeans.labels_]
    cluster_storage.store_cluster(centroids, list(zip(names, embeddings)))
    # TODO: add logging


def give_closest_cluster(text: str, botservice: BotService, cluster_storage: ClusterStorageInterface) -> list[str]:
    """
    Find the closest cluster for the given text based on the embeddings.

    Args:
        text (str): The text to find the closest cluster for.
        botservice (BotService): BotService instance for generating embeddings.

    Returns:
        list[str]: List of names in the closest cluster.
    """
    # shouldn't just attach centroid to embedding bc then need to group clusters evey time during inference instead of
    # just once more intuitive to store clusters as groupings centroid index when using argmin is different from
    # label, labels can be in any order as they correspond to embeddings
    new_embedding = np.array(botservice.embed(texts=[text])[0])

    cluster = cluster_storage.retrieve_cluster()
    centroids = np.array(list(cluster.keys()))

    distances = np.linalg.norm(centroids - new_embedding, axis=1)
    closest_cluster = [value[0] for value in cluster[tuple(centroids[np.argmin(distances)])]]
    # TODO: add logging

    return closest_cluster

# delete_cluster()

# print(give_closest_cluster(['I am autistic'])[1][0])
