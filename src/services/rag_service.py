"""RAG (Retrieval-Augmented Generation) service using ChromaDB."""

import os
import json
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import settings
from database.connection import SessionLocal
from models import ProductKnowledge


class RAGService:
    """RAG service for product knowledge retrieval."""
    
    def __init__(self):
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=settings.vector_db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="product_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize knowledge base
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize the knowledge base with existing data."""
        db = SessionLocal()
        try:
            # Check if collection is empty
            if self.collection.count() == 0:
                print("Initializing RAG knowledge base...")
                
                # Get all product knowledge from database
                knowledge_items = db.query(ProductKnowledge).all()
                
                if knowledge_items:
                    # Prepare data for ChromaDB
                    documents = []
                    metadatas = []
                    ids = []
                    
                    for item in knowledge_items:
                        documents.append(item.content)
                        metadatas.append({
                            "product_id": item.product_id,
                            "knowledge_type": item.knowledge_type,
                            "language": item.language,
                            "id": item.id
                        })
                        ids.append(str(item.id))
                    
                    # Add to ChromaDB
                    self.collection.add(
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
                    
                    print(f"Added {len(knowledge_items)} knowledge items to RAG system")
                else:
                    print("No knowledge items found in database")
        except Exception as e:
            print(f"Error initializing knowledge base: {e}")
        finally:
            db.close()
    
    def add_knowledge(self, content: str, product_id: str, knowledge_type: str, language: str = "en") -> str:
        """Add new knowledge to the RAG system."""
        db = SessionLocal()
        try:
            # Add to database first
            knowledge_item = ProductKnowledge(
                product_id=product_id,
                knowledge_type=knowledge_type,
                content=content,
                language=language
            )
            db.add(knowledge_item)
            db.commit()
            db.refresh(knowledge_item)
            
            # Add to ChromaDB
            self.collection.add(
                documents=[content],
                metadatas=[{
                    "product_id": product_id,
                    "knowledge_type": knowledge_type,
                    "language": language,
                    "id": knowledge_item.id
                }],
                ids=[str(knowledge_item.id)]
            )
            
            return str(knowledge_item.id)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def search_knowledge(
        self, 
        query: str, 
        product_id: Optional[str] = None,
        knowledge_type: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search knowledge base using semantic similarity."""
        try:
            # Build where clause for filtering
            where_clause = {}
            if product_id:
                where_clause["product_id"] = product_id
            if knowledge_type:
                where_clause["knowledge_type"] = knowledge_type
            if language:
                where_clause["language"] = language
            
            # Search in ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            # Format results
            knowledge_items = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    knowledge_items.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if results['distances'] else None
                    })
            
            return knowledge_items
            
        except Exception as e:
            print(f"Error searching knowledge: {e}")
            return []
    
    def get_product_knowledge(self, product_id: str, knowledge_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all knowledge for a specific product."""
        try:
            where_clause = {"product_id": product_id}
            if knowledge_type:
                where_clause["knowledge_type"] = knowledge_type
            
            results = self.collection.get(
                where=where_clause
            )
            
            knowledge_items = []
            if results['documents']:
                for i, doc in enumerate(results['documents']):
                    knowledge_items.append({
                        "content": doc,
                        "metadata": results['metadatas'][i],
                        "id": results['ids'][i]
                    })
            
            return knowledge_items
            
        except Exception as e:
            print(f"Error getting product knowledge: {e}")
            return []
    
    def update_knowledge(self, knowledge_id: str, new_content: str) -> bool:
        """Update existing knowledge item."""
        try:
            # Update in ChromaDB
            self.collection.update(
                ids=[knowledge_id],
                documents=[new_content]
            )
            
            # Update in database
            db = SessionLocal()
            try:
                knowledge_item = db.query(ProductKnowledge).filter(
                    ProductKnowledge.id == knowledge_id
                ).first()
                
                if knowledge_item:
                    knowledge_item.content = new_content
                    db.commit()
                    return True
                return False
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error updating knowledge: {e}")
            return False
    
    def delete_knowledge(self, knowledge_id: str) -> bool:
        """Delete knowledge item."""
        try:
            # Delete from ChromaDB
            self.collection.delete(ids=[knowledge_id])
            
            # Delete from database
            db = SessionLocal()
            try:
                knowledge_item = db.query(ProductKnowledge).filter(
                    ProductKnowledge.id == knowledge_id
                ).first()
                
                if knowledge_item:
                    db.delete(knowledge_item)
                    db.commit()
                    return True
                return False
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error deleting knowledge: {e}")
            return False
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        try:
            total_count = self.collection.count()
            
            # Get knowledge type distribution
            results = self.collection.get()
            knowledge_types = {}
            languages = {}
            
            if results['metadatas']:
                for metadata in results['metadatas']:
                    k_type = metadata.get('knowledge_type', 'unknown')
                    lang = metadata.get('language', 'unknown')
                    
                    knowledge_types[k_type] = knowledge_types.get(k_type, 0) + 1
                    languages[lang] = languages.get(lang, 0) + 1
            
            return {
                "total_items": total_count,
                "knowledge_types": knowledge_types,
                "languages": languages
            }
            
        except Exception as e:
            print(f"Error getting knowledge stats: {e}")
            return {"total_items": 0, "knowledge_types": {}, "languages": {}}
    
    def search_similar_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for products based on knowledge content."""
        try:
            # Search knowledge base
            knowledge_results = self.search_knowledge(query, limit=limit * 2)
            
            # Group by product_id and get unique products
            products = {}
            for result in knowledge_results:
                product_id = result['metadata']['product_id']
                if product_id not in products:
                    products[product_id] = {
                        "product_id": product_id,
                        "knowledge_items": [],
                        "relevance_score": 0
                    }
                
                products[product_id]['knowledge_items'].append(result)
                # Use distance as relevance score (lower is better)
                if result['distance'] is not None:
                    products[product_id]['relevance_score'] += (1 - result['distance'])
            
            # Sort by relevance score and return top results
            sorted_products = sorted(
                products.values(),
                key=lambda x: x['relevance_score'],
                reverse=True
            )
            
            return sorted_products[:limit]
            
        except Exception as e:
            print(f"Error searching similar products: {e}")
            return []
    
    def get_storage_tips(self, product_name: str) -> List[str]:
        """Get storage tips for a specific product."""
        tips = self.search_knowledge(
            f"storage tips for {product_name}",
            knowledge_type="storage",
            limit=3
        )
        
        return [tip['content'] for tip in tips]
    
    def get_nutritional_info(self, product_name: str) -> List[str]:
        """Get nutritional information for a specific product."""
        nutrition = self.search_knowledge(
            f"nutritional information calories {product_name}",
            knowledge_type="nutrition",
            limit=3
        )
        
        return [info['content'] for info in nutrition]
    
    def get_recipes(self, product_name: str) -> List[str]:
        """Get recipes using a specific product."""
        recipes = self.search_knowledge(
            f"recipes using {product_name}",
            knowledge_type="recipe",
            limit=3
        )
        
        return [recipe['content'] for recipe in recipes]
    
    def get_seasonal_info(self, product_name: str) -> List[str]:
        """Get seasonal information for a specific product."""
        seasonal = self.search_knowledge(
            f"seasonal information {product_name}",
            knowledge_type="seasonal",
            limit=3
        )
        
        return [info['content'] for info in seasonal]
