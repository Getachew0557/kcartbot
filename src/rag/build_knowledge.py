import pandas as pd
from src.rag.vector_store import VectorStore

def build_knowledge_base():
    """Build the vector knowledge base from CSV"""
    knowledge_df = pd.read_csv("data/knowledge.csv")
    vector_store = VectorStore()
    vector_store.add_knowledge(knowledge_df)
    print("Knowledge base built successfully!")

if __name__ == "__main__":
    build_knowledge_base()