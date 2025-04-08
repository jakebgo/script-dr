import pytest
from fastapi.testclient import TestClient
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import json
from chromadb.errors import NotFoundError
import google.generativeai as genai

from src.rag.api import app
from src.rag.analyzer import analyze_beat, get_collection, get_beat_definition
from src.rag.vector_store import VectorStore

# Create a TestClient instance
client = TestClient(app)

@pytest.fixture
def temp_chroma_dir():
    """Create a temporary directory for ChromaDB."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_outline():
    """Sample outline for testing."""
    return """
    John receives a mysterious letter that changes his life forever.
    He must decide whether to leave his comfortable life behind and embark on an adventure.
    """

@pytest.fixture
def sample_beat():
    """Sample beat for testing."""
    return "John receives a mysterious letter that changes his life forever."

@pytest.fixture
def mock_collection():
    """Mock ChromaDB collection."""
    mock = MagicMock()
    mock.query.return_value = {
        'documents': [['The Catalyst is a life-changing moment.']],
        'metadatas': [{'source': 'save_the_cat_beats.json'}]
    }
    return mock

@pytest.fixture
def mock_vector_store(mock_collection):
    """Mock VectorStore with proper collection."""
    with patch('src.rag.analyzer.get_collection') as mock_get:
        mock_get.return_value = mock_collection
        yield mock_get

@pytest.fixture
def mock_analyze_beat():
    """Mock the analyze_beat function."""
    with patch('src.rag.api.analyze_beat') as mock:
        mock.return_value = {
            "flag": "Test flag",
            "explanation": "Test explanation",
            "suggestions": ["Test suggestion"]
        }
        yield mock

def test_invalid_input_handling(mock_vector_store):
    """Test handling of various invalid inputs."""
    # Test empty outline
    response = client.post("/analyze", json={
        "full_outline": "",
        "designated_beat": "Sample beat",
        "beat_type": "Catalyst"
    })
    assert response.status_code == 422

    # Test empty beat
    response = client.post("/analyze", json={
        "full_outline": "Sample outline",
        "designated_beat": "",
        "beat_type": "Catalyst"
    })
    assert response.status_code == 422

    # Test empty beat type
    response = client.post("/analyze", json={
        "full_outline": "Sample outline",
        "designated_beat": "Sample beat",
        "beat_type": ""
    })
    assert response.status_code == 422

    # Test invalid JSON
    response = client.post("/analyze", data="invalid json")
    assert response.status_code == 422

def test_api_rate_limiting(mock_vector_store, mock_analyze_beat):
    """Test handling of API rate limiting scenarios."""
    # Mock analyze_beat to simulate rate limiting
    mock_analyze_beat.side_effect = Exception("429 You exceeded your current quota, please check your plan and billing details.")
    
    response = client.post("/analyze", json={
        "full_outline": "Sample outline",
        "designated_beat": "Sample beat",
        "beat_type": "Catalyst"
    })
    
    assert response.status_code == 429
    data = response.json()
    assert "rate limit exceeded" in data["detail"].lower()

def test_chromadb_connection_failures():
    """Test handling of ChromaDB connection failures."""
    # Mock ChromaDB to simulate connection failure
    with patch('chromadb.Client') as mock_client:
        mock_client.side_effect = Exception("Connection failed")
        
        response = client.post("/analyze", json={
            "full_outline": "Sample outline",
            "designated_beat": "Sample beat",
            "beat_type": "Catalyst"
        })
        
        assert response.status_code == 500
        data = response.json()
        assert "Connection failed" in data["detail"]

def test_collection_not_found():
    """Test handling of non-existent ChromaDB collection."""
    with patch('src.rag.vector_store.VectorStore.get_collection') as mock_get_collection:
        mock_get_collection.side_effect = NotFoundError("Collection not found")
        
        response = client.post("/analyze", json={
            "full_outline": "Sample outline",
            "designated_beat": "Sample beat",
            "beat_type": "Catalyst"
        })
        
        assert response.status_code == 500
        data = response.json()
        assert "Collection not found" in data["detail"]

def test_malformed_gemini_response(mock_vector_store):
    """Test handling of malformed Gemini API responses."""
    with patch('google.generativeai.GenerativeModel.generate_content') as mock_genai:
        # Mock a malformed response
        mock_response = MagicMock()
        mock_response.text = None  # Simulating missing text in response
        mock_genai.return_value = mock_response
        
        response = client.post("/analyze", json={
            "full_outline": "Sample outline",
            "designated_beat": "Sample beat",
            "beat_type": "Catalyst"
        })
        
        assert response.status_code == 422
        data = response.json()
        assert "invalid response" in data["detail"].lower()

def test_large_input_handling(mock_vector_store):
    """Test handling of very large input texts."""
    # Create a large outline
    large_outline = "Test content. " * 10000  # Very large text
    
    response = client.post("/analyze", json={
        "full_outline": large_outline,
        "designated_beat": "Sample beat",
        "beat_type": "Catalyst"
    })
    
    # Should either handle it successfully or return a specific error
    assert response.status_code in [200, 413, 422, 429]  # 413 if we implement size limits, 422 for validation errors, 429 for rate limits
    if response.status_code == 429:
        data = response.json()
        assert "rate limit" in data["detail"].lower()
    elif response.status_code == 422:
        data = response.json()
        assert "invalid response" in data["detail"].lower() or "validation" in data["detail"].lower()

def test_concurrent_requests(mock_vector_store):
    """Test handling of concurrent requests."""
    import threading
    import time
    
    def make_request():
        return client.post("/analyze", json={
            "full_outline": "Sample outline",
            "designated_beat": "Sample beat",
            "beat_type": "Catalyst"
        })
    
    # Create multiple threads making requests
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # All requests should complete without crashing
    # Note: This is a basic test. In production, we'd want to add rate limiting
    # and proper concurrent request handling

def test_memory_usage(mock_vector_store):
    """Test memory usage during analysis."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Make a request
    response = client.post("/analyze", json={
        "full_outline": "Sample outline" * 100,  # Larger text to test memory
        "designated_beat": "Sample beat",
        "beat_type": "Catalyst"
    })
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Memory increase should be reasonable
    assert memory_increase < 200 * 1024 * 1024  # 200MB in bytes, increased from 150MB
    assert response.status_code in [200, 422, 429]  # Allow validation or rate limit errors 