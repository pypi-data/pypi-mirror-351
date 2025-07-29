from typing import Dict, List, Optional, Any, Tuple
from sentence_transformers import SentenceTransformer, util
import uuid, os, math
from urllib.parse import urlparse
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, Filter
import logging

# Add timestamps to logging with a specific format
logging.basicConfig(
    level=logging.DEBUG,  # Change to WARNING to reduce verbosity
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class VectorDB:
    def __init__(
        self,
        collection_name: str = "documents",
        model_name: str = "all-MiniLM-L6-v2",   # this is only a fallback name
        model_path: Optional[str] = None,       # local folder with your model
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        qdrant_path: Optional[str] = None,
        qdrant_timeout: Optional[float] = 500,
    ):
        """Initialize the vector database connection with Qdrant

        Args:
            collection_name: Name for the Qdrant collection
            model_name: Name of the sentence-transformer model to use
            model_path: Local folder with your model
            qdrant_url: URL for Qdrant cloud (if using cloud)
            qdrant_api_key: API key for Qdrant cloud (if using cloud)
            qdrant_path: Path for local Qdrant database (if using local)
            qdrant_timeout: Request timeout for Qdrant in seconds (default: 500)
        """
        self.collection_name = collection_name
        
        # Load model: try local first, then fall back to download
        model_source = model_path or model_name
        try:
            logging.info(f"Loading local model '{model_source}'")
            self.model = SentenceTransformer(model_source, local_files_only=True)
        except OSError:
            logging.info(f"Local model '{model_source}' not found—downloading from Hugging Face")
            self.model = SentenceTransformer(model_source)  # will fetch online
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        # Connect to Qdrant (cloud or local)
        if qdrant_url and qdrant_api_key:
            # parse URL and default ports
            parsed = urlparse(qdrant_url)
            scheme = parsed.scheme or "http"
            host = parsed.hostname
            port = parsed.port or (443 if scheme == "https" else 80)
            # build full URL including port
            full_url = f"{scheme}://{host}:{port}"

            self.client = QdrantClient(
                url=full_url,
                api_key=qdrant_api_key,
                prefer_grpc=False,
                timeout=qdrant_timeout or 120.0
            )
        else:
            # Use in-memory or local path
            self.client = QdrantClient(path=qdrant_path)

        # Check if collection exists, create if not
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE),
            )
    
    # NEW METHODS FOR COLLECTION MANAGEMENT
    
    def list_collections(self) -> List[str]:
        """List all collections in the database.
        
        Returns:
            List of collection names
        """
        collections = self.client.get_collections()
        return [collection.name for collection in collections.collections if collection.name]
    
    def delete_collection(self, collection_name: Optional[str] = None) -> bool:
        """Completely delete a collection from the database.
        
        Args:
            collection_name: Name of collection to delete (defaults to current collection)
            
        Returns:
            True if successful, False otherwise
        """
        name = collection_name or self.collection_name
        try:
            self.client.delete_collection(collection_name=name)
            logging.info(f"Collection '{name}' has been deleted")
            return True
        except Exception as e:
            logging.error(f"Failed to delete collection '{name}': {e}")
            return False
    
    def purge_collection(self, collection_name: Optional[str] = None) -> bool:
        """Delete all points from a collection but keep its structure.
        
        Args:
            collection_name: Name of collection to purge (defaults to current collection)
            
        Returns:
            True if successful, False otherwise
        """
        name = collection_name or self.collection_name
        try:
            self.client.delete(
                collection_name=name,
                points_selector=Filter(must=[]),  # Empty filter = all points
            )
            logging.info(f"Collection '{name}' has been purged (all points deleted)")
            return True
        except Exception as e:
            logging.error(f"Failed to purge collection '{name}': {e}")
            return False
    
    def get_collection_stats(self, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics about a collection.
        
        Args:
            collection_name: Name of collection (defaults to current collection)
            
        Returns:
            Dictionary with collection statistics
        """
        name = collection_name or self.collection_name
        try:
            # Get collection info
            collection_info = self.client.get_collection(collection_name=name)
            # Count points
            count_result = self.client.count(collection_name=name, exact=True)
            
            stats = {
                "name": name,
                "status": collection_info.status,
                "vectors_count": count_result.count,
                "vector_size": collection_info.config.params.size,
                "distance": str(collection_info.config.params.distance),
                "indexed": collection_info.config.params.on_disk,
            }
            
            return stats
        except Exception as e:
            logging.error(f"Failed to get stats for collection '{name}': {e}")
            return {"name": name, "error": str(e)}

    # ORIGINAL METHODS BELOW
    
    def chunk_text(self, text: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
        """Split text into chunks with overlap
        
        Args:
            text: The text to chunk
            chunk_size: Size of each chunk in words
            overlap: Number of overlapping words between chunks
        
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
            if i + chunk_size >= len(words):
                break
                
        return chunks
    
    def add_documents(
        self,
        documents: Dict[str, str],
        chunk_size: int = 200,
        overlap: int = 50,
    ):
        """Parse, chunk, and add documents to the vector database
        
        Args:
            documents: Dictionary mapping document names to their text content
            chunk_size: Size of each chunk in words
            overlap: Number of overlapping words between chunks
        """
        points = []
        chunks_per_doc = {}  # Track chunks per document
        
        print(f"Processing {len(documents)} documents...")
        
        for name, text in documents.items():
            chunks = self.chunk_text(text, chunk_size, overlap)
            chunks_per_doc[name] = len(chunks)
            
            print(f"Document '{name}': {len(chunks)} chunks")
            
            for i, chunk in enumerate(chunks):
                # Generate embedding
                embedding = self.model.encode(chunk).tolist()
                
                # Create point
                points.append(
                    models.PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={
                            "document": name,
                            "chunk_id": i,
                            "text": chunk
                        }
                    )
                )
        
        print(f"\nTotal chunks to upload: {len(points)}")
        
        # Add to Qdrant
        # upload in smaller batches to avoid server timeouts
        batch_size = 500
        total = len(points)
        num_batches = math.ceil(total/batch_size)
        
        print(f"Uploading in {num_batches} batches (max {batch_size} chunks per batch)...\n")
        
        for i in range(0, total, batch_size):
            batch = points[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            print(f"Uploading batch {batch_num}/{num_batches} ({len(batch)} chunks)...")
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
        
        print(f"\nSuccessfully added {len(points)} chunks from {len(documents)} documents")
        
        # Print per-document breakdown
        print("\nChunks per document:")
        for name, count in chunks_per_doc.items():
            print(f"- {name}: {count} chunks")
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve relevant chunks for a query
        
        Args:
            query: The query text
            k: Number of results to return
        
        Returns:
            List of relevant chunks with metadata
        """
        query_vector = self.model.encode(query).tolist()
        
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=k
        )
        
        results = []
        for result in search_results:
            data = result.payload
            data["score"] = result.score
            results.append(data)
        
        return results