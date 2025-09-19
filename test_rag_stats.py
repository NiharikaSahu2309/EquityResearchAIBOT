#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.simple_rag import SimpleRAGPipeline

def test_rag_stats():
    print("Testing RAG Statistics...")
    
    # Initialize RAG pipeline
    rag = SimpleRAGPipeline()
    
    # Get stats
    stats = rag.get_collection_stats()
    print(f"RAG Stats: {stats}")
    
    # Check if documents are loaded
    print(f"Documents in memory: {len(rag.documents)}")
    
    if rag.documents:
        print("\nDocument Details:")
        for doc_id, doc_info in rag.documents.items():
            print(f"  - {doc_info['filename']}: {len(doc_info['chunks'])} chunks")
    
    return stats

if __name__ == "__main__":
    test_rag_stats()
