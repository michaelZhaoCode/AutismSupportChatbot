#!/usr/bin/env python3
"""
setup_pinecone.py

Quick setup script for Pinecone storage.
"""

import os
import sys
from dotenv import load_dotenv
from db_funcs.unified_pinecone_storage import UnifiedPineconeStorage

def main():
    """Setup Pinecone storage."""
    print("Pinecone Setup")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    if not os.environ.get('PINECONE_API_KEY'):
        print("\nError: PINECONE_API_KEY not found")
        print("Add to your .env file:")
        print("PINECONE_API_KEY=your_api_key_here")
        sys.exit(1)
    
    try:
        print("\nConnecting to Pinecone...")
        storage = UnifiedPineconeStorage()
        print("✓ Connected successfully")
        
        # Get stats
        stats = storage.get_stats()
        print(f"\nCurrent chunks: {stats['total_chunks']}")
        
        # Optional cleanup
        if stats['total_chunks'] > 0:
            response = input("\nDelete existing chunks? (yes/no): ")
            if response.lower() == 'yes':
                storage.delete_all_chunks()
                print("✓ Chunks deleted")
        
        print("\nSetup complete!")
        print("\nNote: Using modern Pinecone API (v3+)")
        print("Embeddings are generated externally")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("1. Check your PINECONE_API_KEY")
        print("2. Ensure pinecone-client>=3.0.0 is installed")
        sys.exit(1)

if __name__ == "__main__":
    main() 