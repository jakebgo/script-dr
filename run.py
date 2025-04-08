import uvicorn
import os
from dotenv import load_dotenv
from src.rag.document_loader import DocumentLoader
from src.rag.vector_store import VectorStore
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def ingest_framework_document():
    """One-time ingestion of the framework document."""
    try:
        # Initialize vector store
        vector_store = VectorStore()
        
        # Initialize document loader
        loader = DocumentLoader(vector_store)
        
        # Path to the framework document
        framework_path = os.path.join("data", "save_the_cat.pdf")
        
        # Check if the document exists
        if not os.path.exists(framework_path):
            logger.warning(f"Framework document not found at {framework_path}")
            return False
            
        # Load and index the framework document
        logger.info(f"Ingesting framework document from {framework_path}")
        loader.load_framework_document(framework_path)
        logger.info("Framework document ingestion complete")
        return True
    except Exception as e:
        logger.error(f"Error ingesting framework document: {e}")
        return False

if __name__ == "__main__":
    # Ensure the static directory exists
    static_dir = os.path.join(os.path.dirname(__file__), "src", "static")
    os.makedirs(static_dir, exist_ok=True)
    
    # Ensure the data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Ingest the framework document if needed
    ingest_framework_document()
    
    # Run the FastAPI application
    uvicorn.run("src.rag.api:app", host="0.0.0.0", port=8000, reload=True) 