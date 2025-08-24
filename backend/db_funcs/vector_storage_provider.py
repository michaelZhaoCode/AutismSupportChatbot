from abc import ABC, abstractmethod


class VectorStorageProvider(ABC):
    """
    Abstract interface for managing vector embeddings and chunk storage.
    """

    @abstractmethod
    def store_pdf_chunks(self, chunks_data: list[tuple[str, str, list[float]]]) -> None:
        """
        Store chunks with their embeddings.
        
        Args:
            chunks_data: List of tuples (chunk_id, chunk_text, embedding)
        """
        pass

    @abstractmethod
    def retrieve_similar_chunks(self, 
                              query_embedding: list[float], 
                              top_k: int = 10,
                              filter_dict: dict = None) -> list[dict]:
        """
        Retrieve similar chunks using vector similarity search.
        
        Args:
            query_embedding: Query vector for similarity search
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of dicts with chunk information and similarity scores
        """
        pass

    @abstractmethod
    def get_chunk_by_id(self, chunk_id: str) -> dict:
        """
        Retrieve a specific chunk by ID.
        
        Args:
            chunk_id: ID of the chunk to retrieve
            
        Returns:
            Chunk data or None if not found
        """
        pass

    @abstractmethod
    def delete_chunks(self, chunk_ids: list[str]) -> None:
        """
        Delete specific chunks by their IDs.
        
        Args:
            chunk_ids: List of chunk IDs to delete
        """
        pass

    @abstractmethod
    def get_relevant_chunks(self, prompt_embedding: list[float], top_k: int = 5) -> list[tuple[str, str]]:
        """
        Get the most relevant chunks for the given prompt using similarity search.

        Args:
            prompt_embedding: The user's prompt embedding to find relevant chunks for.
            top_k: Number of most relevant chunks to retrieve.

        Returns:
            List of tuples (chunk_id, chunk_text) for the most relevant chunks.
        """
        pass

    @abstractmethod
    def delete_all_chunks(self) -> None:
        """Delete all chunks from the storage."""
        pass

    @abstractmethod
    def update_chunk(self, chunk_id: str, new_text: str, new_embedding: list[float]) -> None:
        """
        Update a specific chunk's text and embedding.
        
        Args:
            chunk_id: ID of the chunk to update
            new_text: New text content
            new_embedding: New embedding vector
        """
        pass

    @abstractmethod
    def get_stats(self) -> dict:
        """
        Get statistics about the storage.
        
        Returns:
            Dictionary with storage statistics
        """
        pass
