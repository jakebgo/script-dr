#!/usr/bin/env python3
"""
Script to re-ingest the Save the Cat framework document with improved beat separation.
This addresses the UAT issue where beats like "All Is Lost" and "Dark Night of the Soul" were confused.
"""

import os
import sys
import logging
from pathlib import Path
from src.rag.document_loader import DocumentLoader
from src.rag.vector_store import VectorStore
from src.config.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('reingest_log.txt')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    Main function to re-ingest the Save the Cat framework document.
    """
    try:
        logger.info("Starting re-ingestion of Save the Cat framework document")
        
        # Initialize configuration
        config = Config()
        
        # Initialize vector store
        vector_store = VectorStore()
        
        # Initialize document loader
        loader = DocumentLoader(vector_store)
        
        # Path to the framework document
        data_dir = Path("data")
        framework_path = data_dir / "save_the_cat.pdf"
        
        # Check if the document exists
        if not framework_path.exists():
            logger.error(f"Framework document not found at {framework_path}")
            sys.exit(1)
            
        # Load and index the framework document
        logger.info(f"Re-ingesting framework document from {framework_path}")
        loader.load_framework_document(str(framework_path))
        
        # Test the retrieval
        logger.info("Testing beat retrieval")
        
        # Get the collection
        collection = vector_store.get_collection("save_the_cat")
        
        # Test some problematic beat types
        test_beats = ["All Is Lost", "Dark Night of the Soul", "Midpoint", "Break Into Two"]
        
        for beat_type in test_beats:
            logger.info(f"Testing retrieval for '{beat_type}'")
            
            # Test query directly on collection
            results = collection.query(
                query_texts=[f"What is the definition of the {beat_type} beat?"],
                n_results=1,
                where={"beat_type": beat_type}
            )
            
            if results["documents"] and results["documents"][0]:
                logger.info(f"Found definition for {beat_type}: {results['documents'][0][0][:100]}...")
                logger.info(f"Metadata: {results['metadatas'][0][0]}")
            else:
                logger.warning(f"No definition found for {beat_type}")
        
        logger.info("Re-ingestion complete")
        return True
    except Exception as e:
        logger.error(f"Error re-ingesting framework document: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 