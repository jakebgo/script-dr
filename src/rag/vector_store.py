import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Any
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize the vector store with ChromaDB.
        
        Args:
            persist_directory (str): Directory to persist the vector store
        """
        self.persist_directory = persist_directory
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        
    def create_collection(self, name: str, metadata: Dict[str, Any] = None) -> chromadb.Collection:
        """Create a new collection in the vector store.
        
        Args:
            name (str): Name of the collection
            metadata (Dict[str, Any], optional): Metadata for the collection
            
        Returns:
            chromadb.Collection: The created collection
        """
        # If collection exists, delete it first
        if self.collection_exists(name):
            logger.info(f"Collection {name} already exists. Deleting it.")
            self.delete_collection(name)
            
        return self.client.create_collection(name=name, metadata=metadata)
    
    def get_collection(self, name: str) -> chromadb.Collection:
        """Get an existing collection by name.
        
        Args:
            name (str): Name of the collection
            
        Returns:
            chromadb.Collection: The requested collection
        """
        return self.client.get_collection(name=name)
    
    def collection_exists(self, name: str) -> bool:
        """Check if a collection exists.
        
        Args:
            name (str): Name of the collection
            
        Returns:
            bool: True if the collection exists, False otherwise
        """
        try:
            self.get_collection(name)
            return True
        except Exception:
            return False
    
    def list_collections(self) -> List[str]:
        """List all collections in the vector store.
        
        Returns:
            List[str]: List of collection names
        """
        collections = self.client.list_collections()
        return [collection.name for collection in collections]
    
    def delete_collection(self, name: str) -> None:
        """Delete a collection from the vector store.
        
        Args:
            name (str): Name of the collection to delete
        """
        try:
            self.client.delete_collection(name=name)
            logger.info(f"Collection {name} deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting collection {name}: {str(e)}")
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        ids: List[str],
        metadatas: List[Dict[str, Any]] = None
    ) -> None:
        """Add documents to a collection.
        
        Args:
            collection_name (str): Name of the collection
            documents (List[str]): List of document texts
            ids (List[str]): List of document IDs
            metadatas (List[Dict[str, Any]], optional): List of metadata dictionaries
        """
        collection = self.get_collection(collection_name)
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
    
    def query(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5,
        where: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Query the vector store.
        
        Args:
            collection_name (str): Name of the collection to query
            query_text (str): Query text
            n_results (int): Number of results to return
            where (Dict[str, Any], optional): Filter conditions
            
        Returns:
            Dict[str, Any]: Query results containing documents, distances, and metadata
        """
        collection = self.get_collection(collection_name)
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where
        )
        return results

# Global function to get a collection by name
def get_collection(name: str) -> chromadb.Collection:
    """Get a ChromaDB collection by name.
    
    Args:
        name (str): Name of the collection
        
    Returns:
        chromadb.Collection: The requested collection
    """
    vector_store = VectorStore()
    return vector_store.get_collection(name) 