"""
embed.py

This module provides functions to retrieve and calculate embeddings for PDF files using the BotService.
"""
import logging

from api.botservice import BotService
from db_funcs.file_storage import PDFStorageInterface
from db_funcs.cluster_storage import ClusterStorageInterface
from utils import extract_text

logger = logging.getLogger(__name__)


# when user calls insert or bulk insert, we dont need to directly call insert/bulk insert and thats it whatever new
# files are being added, pass those in when re-computing cluster for eg. for first bulkinsert, retireve cluster (it
# will be empty) and then use all of its embeddings + newly computed embeddings for new files this is same process
# for adding to embeddings table, u still need to know when to add embeddings this way it is nicely synced,
# whenever adding files, cluster also recomputed with new files embeddigns calculated

def retrieve_all_embeddings(
        botservice: BotService,
        pdf_storage: PDFStorageInterface,
        cluster_storage: ClusterStorageInterface,
        new_files: list[str] = None,
        is_insert: bool = True
) -> tuple[list[str], list[list[float]]]:
    """
    Retrieve all embeddings, optionally including new files. If new files are added, re-compute the cluster.

    Args:
        botservice (BotService): BotService instance for generating embeddings.
        pdf_storage (PDFStorageInterface): The PDF storage interface instance.
        cluster_storage (ClusterStorageInterface): The cluster storage interface instance.
        new_files (list[str], optional): List of new file names to include in the embeddings. Defaults to None.
        is_insert (bool, optional): Flag to determine whether to insert new embeddings. Defaults to True.

    Returns:
        tuple[list[str], list[list[float]]]: A tuple containing a list of file names and their corresponding embeddings.
    """
    if not new_files:
        new_files = list()
    logger.debug("retrieve_all_embeddings: Retrieving cluster data")
    cluster = cluster_storage.retrieve_cluster()

    names = []
    embeddings = []
    for centroid in cluster:
        for name, embedding in cluster[centroid]:
            names.append(name)
            embeddings.append(embedding)
    if is_insert:
        logger.info("retrieve_all_embeddings: Calculating new embeddings to insert")
        new_embeddings = calc_embeddings(new_files, botservice, pdf_storage)
        names.extend(new_files)
        embeddings.extend(new_embeddings)
    else:
        logger.info("retrieve_all_embeddings: New embeddings not inserted (is_insert=False)")
        files_set = set(new_files)
        new_names = []
        new_embeddings = []
        for name in names:
            if name not in files_set:
                new_names.append(name)
                new_embeddings.append(calc_embeddings([name], botservice, pdf_storage)[0])
    logger.info("retrieve_all_embeddings: Returning names and embeddings")
    return names, embeddings


def calc_embeddings(file_names: list[str], botservice: BotService, pdf_storage: PDFStorageInterface) -> list[
        list[float]]:
    """
    Calculate embeddings for the given list of file names using the BotService.

    Args:
        file_names (list[str]): List of file names to calculate embeddings for.
        botservice (BotService): BotService instance for generating embeddings.
        pdf_storage (PDFStorageInterface): The PDF storage interface instance.

    Returns:
        list[list[float]]: A list of embeddings for the provided file names.
    """
    file_content = pdf_storage.retrieve_pdfs(file_names)
    file_texts = [extract_text(content) for content in file_content]
    logger.info("calc_embeddings: Retrieved PDFs and extracted text")
    embeddings = botservice.embed(texts=file_texts)
    logger.info("calc_embeddings: Calculated embeddings for PDF texts")
    return embeddings
