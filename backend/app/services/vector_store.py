"""Vector store service for Qdrant operations."""
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import settings
from app.services.ingestion import get_document_id
import uuid
import re

class VectorStore:
    """Service for managing vector store operations with Qdrant."""
    
    def __init__(self):
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            url=settings.qdrant_url,
            timeout=300  # Increased timeout for large batch operations
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
    
    def create_collection(self, vector_size: int = 1024):
        """
        Create a new collection in Qdrant with optimized configuration.
        
        Args:
            vector_size: Size of the embedding vectors
        """
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                ),
                optimizers_config={
                    "indexing_threshold": 10000,  # Index after 10k points
                    "memmap_threshold": 20000,     # Use memmap for large collections
                }
            )
            print(f"Collection '{self.collection_name}' created successfully.")
            
            # Create payload indexes for common filter fields
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="Department",
                    field_schema="keyword"
                )
                print("Created index for 'Department' field")
            except Exception as e:
                if "already exists" not in str(e).lower():
                    print(f"Warning: Could not create Department index: {e}")
            
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="Company",
                    field_schema="keyword"
                )
                print("Created index for 'Company' field")
            except Exception as e:
                if "already exists" not in str(e).lower():
                    print(f"Warning: Could not create Company index: {e}")
                    
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"Collection '{self.collection_name}' already exists.")
            else:
                raise
    
    def collection_exists(self) -> bool:
        """Check if the collection exists."""
        try:
            collections = self.client.get_collections()
            return any(c.name == self.collection_name for c in collections.collections)
        except Exception:
            return False
    
    def is_connected(self) -> bool:
        """Check if Qdrant is accessible."""
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False
    
    def upsert_documents(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        batch_size: int = 100
    ):
        """
        Insert or update documents in the collection in batches.
        
        Args:
            embeddings: List of embedding vectors
            documents: List of document texts
            metadatas: List of metadata dictionaries
            batch_size: Number of documents to insert per batch (default: 100)
        """
        total_docs = len(embeddings)
        print(f"Inserting {total_docs} documents in batches of {batch_size}...")
        
        # Process in batches to avoid timeout
        for batch_start in range(0, total_docs, batch_size):
            batch_end = min(batch_start + batch_size, total_docs)
            batch_points = []
            
            for i in range(batch_start, batch_end):
                # Use deterministic ID for deduplication
                doc_id = get_document_id(metadatas[i])
                
                point = PointStruct(
                    id=doc_id,
                    vector=embeddings[i],
                    payload={
                        **metadatas[i],
                        "content": documents[i]
                    }
                )
                batch_points.append(point)
            
            # Insert batch
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch_points
                )
                print(f"Inserted batch {batch_start // batch_size + 1} ({batch_end - batch_start} documents) - Progress: {batch_end}/{total_docs} ({100 * batch_end // total_docs}%)")
            except Exception as e:
                print(f"Error inserting batch {batch_start // batch_size + 1}: {e}")
                raise
        
        print(f"✅ Successfully inserted all {total_docs} documents into collection.")
    
    def _calculate_adaptive_threshold(self, query_text: str, top_k: int) -> float:
        """
        Calculate adaptive score threshold based on query characteristics.
        
        Args:
            query_text: Original query text
            top_k: Number of results requested
            
        Returns:
            Adaptive threshold value
        """
        # Base threshold
        base_threshold = 0.1
        
        # Adjust based on query length
        query_words = len(query_text.split())
        if query_words <= 2:
            # Short queries (e.g., "Györök György") - stricter threshold
            threshold = 0.3
        elif query_words <= 5:
            # Medium queries - moderate threshold
            threshold = 0.15
        else:
            # Long/complex queries - more lenient
            threshold = 0.05
        
        # Adjust based on requested results
        if top_k <= 3:
            threshold += 0.1  # Stricter for fewer results
        elif top_k >= 10:
            threshold -= 0.05  # More lenient for more results
        
        # Ensure threshold is within valid range for cosine similarity
        return max(-1.0, min(0.9, threshold))
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: Optional[float] = None,
        query_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents with adaptive threshold.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            score_threshold: Minimum similarity score (if None, uses adaptive threshold)
            query_text: Original query text for adaptive threshold calculation
            
        Returns:
            List of search results with scores and metadata
        """
        try:
            # Use adaptive threshold if not provided
            if score_threshold is None and query_text:
                score_threshold = self._calculate_adaptive_threshold(query_text, top_k)
            elif score_threshold is None:
                score_threshold = 0.1  # Default fallback
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold
            )
            
            search_results = []
            for result in results:
                search_results.append({
                    "score": result.score,
                    "metadata": result.payload,
                    "content": result.payload.get("content", "")
                })
            
            return search_results
        except Exception as e:
            print(f"Error during search: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def delete_collection(self):
        """Delete the collection (use with caution)."""
        try:
            self.client.delete_collection(self.collection_name)
            print(f"Collection '{self.collection_name}' deleted.")
        except Exception as e:
            print(f"Error deleting collection: {e}")

