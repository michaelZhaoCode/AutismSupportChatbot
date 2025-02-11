"""
cluster_storage.py

This module provides a class to store, retrieve, and delete clustering data in a MongoDB database.
"""
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ClusterStorageInterface:
    """
    A class to interact with clustering data in a MongoDB database.

    This class provides methods to store, retrieve, and delete clustering data
    in a MongoDB database. It requires a MongoDB database object to be passed
    during initialization.

    Attributes:
        db (Database): The MongoDB database object used for storing clustering data.

    Methods:
        store_cluster(centroids: list[list[float]], embeddings_and_names: list[tuple[str, list[float]]]) -> None:
            Stores the centroids and their associated embeddings.

        retrieve_cluster() -> dict[tuple[float, ...], list[tuple[str, list[float]]]]:
            Retrieves the stored clustering data.

        delete_cluster() -> None:
            Deletes the clustering data.
    """

    def __init__(self, db):
        """
        Initializes the ClusterStorageInterface with a MongoDB database object.

        Args:
            db (Database): The MongoDB database object used for storing clustering data.
        """
        self.db = db

    def store_cluster(self, centroids: list[list[float]], embeddings_and_names: list[tuple[str, list[float]]]) -> None:
        """
        Store the centroids and their associated embeddings in the MongoDB database.

        Args:
            centroids (list[list[float]]): A list of centroid coordinates.
            embeddings_and_names (list[tuple[str, list[float]]]): A list of tuples, each containing a name and its
                corresponding embedding.
        """
        clusters_collection = self.db['clusters']

        cluster = defaultdict(list)
        for i in range(len(centroids)):
            centroid = centroids[i]
            embedding_and_name = embeddings_and_names[i]
            cluster[tuple(centroid)].append(embedding_and_name)
            logging.debug("store_cluster: Inserting centroid (%.5f, %.5f) with associated embedding %s",
                          centroid[0], centroid[1], embedding_and_name[0])

        # each embedding is a tuple of (name, embedding val)
        cluster_documents = [
            {
                'centroid': centroid,
                'embedding_and_name': cluster[centroid]
            } for centroid in cluster
        ]

        clusters_collection.insert_many(cluster_documents)
        logging.info("store_cluster: Inserted clustering data into clusters_collection")

    def retrieve_cluster(self) -> dict[tuple[float, ...], list[tuple[str, list[float]]]]:
        """
        Retrieve the stored clustering data from the MongoDB database.

        Returns: dict[tuple[float, ...], list[tuple[str, list[float]]]]: A dictionary where the keys are centroids
            and the values are lists of tuples containing names and embeddings.
        """
        clusters_collection = self.db['clusters']

        cluster = {tuple(document['centroid']): document['embedding_and_name'] for document in
                   clusters_collection.find()}

        logging.info("retrieve_cluster: Retrieved clustering data from the MongoDB database")
        return cluster

    def delete_cluster(self) -> None:
        """
        Delete the clustering data from the MongoDB database.
        """
        self.db.drop_collection('clusters')
        logger.info("delete_cluster: Deleted clustering data from the MongoDB database")


if __name__ == "__main__":
    from utils import setup_mongo_db
    from logger import setup_logger

    setup_logger("db_funcs.log")
    database = setup_mongo_db()
    print("Deleting cluster.")
    cluster_storage_interface = ClusterStorageInterface(database)
    cluster_storage_interface.delete_cluster()
