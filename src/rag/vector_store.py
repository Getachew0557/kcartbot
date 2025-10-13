import chromadb
from chromadb.config import Settings
import pandas as pd
import os

class VectorStore:
    def __init__(self, persist_directory="./.chroma"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="product_knowledge",
            metadata={"description": "Product knowledge base for KcartBot"}
        )
    
    def add_knowledge(self, knowledge_df):
        """Add knowledge base to vector store"""
        documents = []
        metadatas = []
        ids = []
        
        for _, row in knowledge_df.iterrows():
            documents.append(f"Q: {row['question']} A: {row['answer']}")
            metadatas.append({
                "product_id": row['product_id'],
                "language": row['language'],
                "question": row['question']
            })
            ids.append(str(row['id']))
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def query(self, question, n_results=3, language_filter=None):
        """Query the knowledge base"""
        where = {}
        if language_filter:
            where["language"] = language_filter
            
        results = self.collection.query(
            query_texts=[question],
            n_results=n_results,
            where=where
        )
        
        return results

def get_vector_store():
    return VectorStore()