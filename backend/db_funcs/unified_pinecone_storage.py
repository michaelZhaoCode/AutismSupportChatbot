"""
unified_pinecone_storage.py

Simple unified storage system for chunks and their embeddings in Pinecone.
"""

import logging
import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def setup_pinecone():
    """
    Sets up the Pinecone connection and returns the index instance.
    
    Returns:
        Pinecone Index instance for vector operations.
    """
    load_dotenv()
    
    # Initialize Pinecone client
    pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))
    
    index_name = os.environ.get('PINECONE_INDEX_NAME', 'autism-chatbot')
    
    # Create index if it doesn't exist
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=1536,  # Default for text-embedding-3-small
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        logger.info(f"Created new Pinecone index: {index_name}")
    
    index = pc.Index(index_name)
    logger.info(f"Connected to Pinecone index: {index_name}")
    
    return index


class UnifiedPineconeStorage:
    """
    Simple storage for chunks and their embeddings in Pinecone.
    """
    
    def __init__(self, index = None):
        """
        Initialize the storage.
        
        Args:
            index: Pinecone index instance. If None, creates a new one.
        """
        self.index = index or setup_pinecone()
        logger.info("UnifiedPineconeStorage initialized")
    
    def store_pdf_chunks(self, chunks_data: list[tuple[str, str, list[float]]]) -> None:
        """
        Store chunks with their embeddings in Pinecone.
        
        Args:
            chunks_data: List of tuples (chunk_id, chunk_text, embedding)
        """
        if not chunks_data:
            logger.warning("No chunks to store")
            return
        
        vectors_to_upsert = []
        
        for chunk_id, chunk_text, embedding in chunks_data:
            # Store the full chunk text in metadata
            vector_record = {
                'id': chunk_id,
                'values': embedding,
                'metadata': {
                    'text': chunk_text  # Store the full text
                }
            }
            vectors_to_upsert.append(vector_record)
        
        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i+batch_size]
            self.index.upsert(vectors=batch)
            logger.debug(f"Upserted batch {i//batch_size + 1}")
        
        logger.info(f"Stored {len(chunks_data)} chunks with embeddings")
    
    def retrieve_similar_chunks(self, 
                              query_embedding: list[float], 
                              top_k: int = 10,
                              filter_dict: dict = None) -> list[dict]:
        """
        Retrieve similar chunks using Pinecone's ANN algorithm.
        
        Args:
            query_embedding: Query vector for similarity search
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of dicts with chunk information and similarity scores
        """
        query_response = self.index.query(
            vector=query_embedding,
            filter=filter_dict,
            top_k=top_k,
            include_metadata=True,
            include_values=False
        )
        
        results = []
        for match in query_response.matches:
            result = {
                'chunk_id': match['id'],
                'score': match['score'],
                'text': match['metadata'].get('text', ''),
            }
            results.append(result)
        
        logger.info(f"Retrieved {len(results)} similar chunks")
        return results
    
    def get_chunk_by_id(self, chunk_id: str) -> dict:
        """
        Retrieve a specific chunk by ID.
        
        Args:
            chunk_id: ID of the chunk to retrieve
            
        Returns:
            Chunk data or None if not found
        """
        # Fetch by ID
        fetch_response = self.index.fetch(ids=[chunk_id])
        
        if chunk_id in fetch_response.vectors:
            vector_data = fetch_response.vectors[chunk_id]
            return {
                'chunk_id': chunk_id,
                'text': vector_data.metadata.get('text', ''),
            }
        return None
    
    def delete_chunks(self, chunk_ids: list[str]) -> None:
        """
        Delete specific chunks by their IDs.
        
        Args:
            chunk_ids: List of chunk IDs to delete
        """
        if not chunk_ids:
            return
        
        self.index.delete(ids=chunk_ids)
        logger.info(f"Deleted {len(chunk_ids)} chunks")
    
    def get_relevant_chunks(self, prompt_embedding: list[float], top_k: int = 5) -> list[tuple[str, str]]:
        """
        Get the most relevant PDF chunks for the given prompt using similarity search.

        Args:
            prompt_embedding (list[float]): The user's prompt embedding to find relevant chunks for.
            top_k (int): Number of most relevant chunks to retrieve.

        Returns:
            List[Tuple[str, str]]: List of tuples (chunk_id, chunk_text) for the most relevant chunks.
        """
        
        # Retrieve similar chunks using Pinecone's ANN algorithm
        similar_chunks = self.retrieve_similar_chunks(
            query_embedding=prompt_embedding,
            top_k=top_k
        )
        
        # Extract chunk IDs and texts
        relevant_chunks = [
            (chunk['chunk_id'], chunk['text'])
            for chunk in similar_chunks
        ]
        
        logger.info(f"_get_relevant_chunks: Retrieved {len(relevant_chunks)} relevant chunks")
        return relevant_chunks
    
    def delete_all_chunks(self) -> None:
        """Delete all chunks from the index."""
        self.index.delete(delete_all=True)
        logger.info("Deleted all chunks from Pinecone index")
    
    def update_chunk(self, chunk_id: str, new_text: str, new_embedding: list[float]) -> None:
        """
        Update a specific chunk's text and embedding.
        
        Args:
            chunk_id: ID of the chunk to update
            new_text: New text content
            new_embedding: New embedding vector
        """
        self.store_pdf_chunks([(chunk_id, new_text, new_embedding)])
        logger.info(f"Updated chunk: {chunk_id}")
    
    def get_stats(self) -> dict:
        """
        Get statistics about the storage.
        
        Returns:
            Dictionary with storage statistics
        """
        stats = self.index.describe_index_stats()
        return {
            'total_chunks': stats.get('total_vector_count', 0),
            'index_fullness': stats.get('index_fullness', 0),
            'dimension': stats.get('dimension', 0)
        }


if __name__ == "__main__":
    # Example usage
    storage = UnifiedPineconeStorage()
    stats = storage.get_stats()
    print(f"Storage stats: {stats}") 