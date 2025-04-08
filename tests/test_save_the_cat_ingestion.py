import pytest
import os
import tempfile
import shutil
from pathlib import Path
import chromadb
from chromadb.errors import NotFoundError

from src.rag.document_loader import DocumentLoader
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever

@pytest.fixture
def temp_chroma_dir():
    """Create a temporary directory for ChromaDB."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_save_the_cat_pdf():
    """Path to the sample Save the Cat PDF file."""
    return os.path.join("data", "save_the_cat", "savethecat.pdf")

@pytest.fixture
def vector_store(temp_chroma_dir):
    """Create a VectorStore instance with temporary ChromaDB directory."""
    return VectorStore(persist_directory=temp_chroma_dir)

@pytest.fixture
def document_loader(vector_store):
    """Create a DocumentLoader instance."""
    return DocumentLoader(vector_store)

@pytest.fixture
def retriever(vector_store):
    """Create a Retriever instance."""
    return Retriever(vector_store)

def test_save_the_cat_ingestion(document_loader, sample_save_the_cat_pdf):
    """Test that the Save the Cat document is correctly ingested into ChromaDB."""
    # Verify the PDF exists
    assert os.path.exists(sample_save_the_cat_pdf), "Save the Cat PDF not found"
    
    # Ingest the document
    document_loader.load_framework_document(sample_save_the_cat_pdf)
    
    # Verify the collection exists and has content
    assert document_loader.vector_store.collection_exists("save_the_cat")
    collection = document_loader.vector_store.get_collection("save_the_cat")
    assert collection.count() > 0

def test_beat_definition_retrieval(retriever, document_loader, sample_save_the_cat_pdf):
    """Test that beat definitions can be correctly retrieved from ChromaDB."""
    # First ingest the document
    document_loader.load_save_the_cat(os.path.join("data", "save_the_cat", "beats.json"))
    
    # Test retrieving definitions for different beat types
    beat_types = ["Midpoint", "Catalyst", "Break into Two"]
    for beat_type in beat_types:
        # Query for the beat definition
        result = retriever.get_beat_definition(beat_type)
        
        # Verify we got results
        assert result is not None, f"No results found for {beat_type}"
        
        # Verify the results contain relevant content
        assert beat_type.lower() in result["definition"].lower(), \
            f"Retrieved text doesn't contain {beat_type}"
        
        # Verify metadata is present
        assert result["metadata"] is not None, "Missing metadata in result"

def test_chunk_overlap(document_loader, sample_save_the_cat_pdf):
    """Test that document chunks have appropriate overlap for context preservation."""
    document_loader.load_framework_document(sample_save_the_cat_pdf)
    
    # Get all chunks
    collection = document_loader.vector_store.get_collection("save_the_cat")
    chunks = collection.get()
    
    # Verify chunk size and overlap
    for i in range(len(chunks['documents']) - 1):
        current_chunk = chunks['documents'][i]
        next_chunk = chunks['documents'][i + 1]
        
        # Check that chunks are not too large
        assert len(current_chunk) <= 1000, "Chunk size exceeds maximum"
        
        # Check for overlap between consecutive chunks
        overlap = set(current_chunk.split()) & set(next_chunk.split())
        assert len(overlap) >= 100, "Insufficient overlap between chunks" 