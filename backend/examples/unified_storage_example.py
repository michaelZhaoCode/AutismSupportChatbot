"""
unified_storage_example.py

Example usage of the UnifiedPineconeStorage system for chunk storage and retrieval.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_funcs.unified_pinecone_storage import UnifiedPineconeStorage
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()


def example_store_and_retrieve():
    """Example of storing chunks and retrieving similar ones."""
    print("=== Store and Retrieve Example ===\n")
    
    # Create storage instance
    storage = UnifiedPineconeStorage()
    
    # Example chunks data (in real use, these would come from PDFs)
    example_chunks = [
        ("chunk-001", "Autism is a developmental disorder that affects communication and behavior.", np.random.rand(1536).tolist()),
        ("chunk-002", "Early intervention can significantly improve outcomes for children with autism.", np.random.rand(1536).tolist()),
        ("chunk-003", "Behavioral therapy is one of the most effective treatments for autism.", np.random.rand(1536).tolist()),
        ("chunk-004", "Speech therapy helps improve communication skills in autistic children.", np.random.rand(1536).tolist()),
    ]
    
    # Store chunks
    print("Storing chunks...")
    storage.store_pdf_chunks(example_chunks)
    print(f"Stored {len(example_chunks)} chunks\n")
    
    # Search for similar chunks
    print("Searching for chunks related to 'therapy for autism'...")
    query_embedding = np.random.rand(1536).tolist()  # In real use, this would be the embedding of the query
    results = storage.retrieve_similar_chunks(query_embedding, top_k=3)
    
    print("\nSearch Results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Chunk ID: {result['chunk_id']}")
        print(f"   Score: {result['score']:.4f}")
        print(f"   Text: {result['text']}")


def example_chunk_operations():
    """Example of getting, updating, and deleting chunks."""
    print("\n\n=== Chunk Operations Example ===\n")
    
    storage = UnifiedPineconeStorage()
    
    # Get a specific chunk by ID
    chunk_id = "chunk-001"
    print(f"Retrieving chunk: {chunk_id}")
    chunk = storage.get_chunk_by_id(chunk_id)
    if chunk:
        print(f"Found chunk: {chunk['text'][:100]}...")
    else:
        print("Chunk not found")
    
    # Update a chunk
    print(f"\nUpdating chunk: {chunk_id}")
    new_text = "Updated content: Autism spectrum disorder (ASD) is a complex developmental condition."
    new_embedding = np.random.rand(1536).tolist()
    storage.update_chunk(chunk_id, new_text, new_embedding)
    print("Update successful")
    
    # Delete specific chunks
    print("\nDeleting chunks: chunk-003, chunk-004")
    storage.delete_chunks(["chunk-003", "chunk-004"])
    print("Deletion successful")


def example_statistics():
    """Example of getting storage statistics."""
    print("\n\n=== Storage Statistics ===\n")
    
    storage = UnifiedPineconeStorage()
    stats = storage.get_stats()
    
    print("Pinecone Index Statistics:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Index fullness: {stats['index_fullness']:.2%}")
    print(f"  Vector dimension: {stats['dimension']}")


def cleanup_example():
    """Example of cleaning up all data."""
    print("\n\n=== Cleanup Example ===\n")
    
    response = input("Do you want to delete ALL chunks? (yes/no): ")
    if response.lower() == 'yes':
        storage = UnifiedPineconeStorage()
        storage.delete_all_chunks()
        print("All chunks deleted from Pinecone")
    else:
        print("Cleanup cancelled")


if __name__ == "__main__":
    print("Unified Pinecone Storage Examples")
    print("=" * 50)
    
    
 
    # Run examples
    example_store_and_retrieve()
    example_chunk_operations()
    example_statistics()
        
        