import pytest
from fastapi.testclient import TestClient
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import json

from src.rag.api import app
from src.rag.analyzer import analyze_beat, get_collection

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
    """Sample screenplay outline for testing."""
    return """
    ACT ONE
    
    OPENING IMAGE: John Smith, a middle-aged accountant, sits alone in his cubicle, surrounded by paperwork. The camera pans to show rows of identical cubicles, all filled with workers who look just as miserable.
    
    THEME STATED: John's boss, Mr. Johnson, tells him "Life is about taking risks, not playing it safe."
    
    SET-UP: We see John's daily routine - he wakes up early, takes the same route to work, eats the same lunch, and returns home to his empty apartment. His only companion is his goldfish, whom he talks to about his dreams of adventure.
    
    CATALYST: John receives a mysterious letter inviting him to join an exclusive adventure club. The letter promises "the experience of a lifetime" but requires a significant financial investment.
    
    DEBATE: John spends the night researching the club online, reading testimonials, and checking his bank account. He's torn between his desire for adventure and his fear of the unknown.
    
    BREAK INTO TWO: Against his better judgment, John writes a check for the full amount and mails it to the adventure club.
    
    ACT TWO
    
    B STORY: John meets Sarah, a free-spirited travel writer who's also a member of the adventure club. She challenges his conservative worldview and encourages him to embrace uncertainty.
    
    FUN AND GAMES: John participates in increasingly daring adventures - skydiving, rock climbing, and white-water rafting. Each experience pushes him further out of his comfort zone.
    
    MIDPOINT: During a mountain climbing expedition, John faces a life-threatening situation when he get separated from the group during a storm. He must rely on his own resourcefulness to survive.
    
    BAD GUYS CLOSE IN: John's conservative family and friends express concern about his new lifestyle. His boss threatens to fire him if he doesn't return to his old routine. Meanwhile, the adventure club faces financial difficulties and may have to cancel future expeditions.
    
    ALL IS LOST: John learns that the adventure club is actually a scam, and all the "adventures" were staged. His investment is gone, and he feels betrayed and foolish.
    
    DARK NIGHT OF THE SOUL: John returns to his old routine, feeling like a failure. He realizes that he's lost both his money and his newfound confidence.
    
    BREAK INTO THREE: John discovers that Sarah, despite being part of the scam, genuinely cared about him. She offers to help him plan a real adventure using the skills he learned.
    
    ACT THREE
    
    FINALE: John and Sarah organize a legitimate adventure for themselves and other former club members. They use the skills they learned to navigate a challenging wilderness expedition. John finally finds the courage to quit his job and pursue a career as an adventure guide.
    
    FINAL IMAGE: John stands at the top of a mountain, surrounded by a group of clients. He's now the one encouraging others to step out of their comfort zones and embrace life's adventures.
    """

@pytest.fixture
def sample_beat():
    """Sample beat for testing."""
    return "John receives a mysterious letter inviting him to join an exclusive adventure club. The letter promises 'the experience of a lifetime' but requires a significant financial investment."

@pytest.fixture
def mock_analyze_beat():
    """Mock the analyze_beat function to return a predictable result."""
    with patch('src.rag.api.analyze_beat') as mock:
        mock.return_value = {
            "flag": "The Catalyst lacks sufficient emotional impact",
            "explanation": "According to Save the Cat, the Catalyst should create a significant emotional reaction in the protagonist that forces them to consider change.",
            "suggestions": [
                "Add more personal stakes to the letter - perhaps it mentions something from John's past",
                "Include a time limit to create urgency",
                "Show John's immediate emotional reaction to receiving the letter"
            ]
        }
        yield mock

@pytest.fixture
def mock_get_collection():
    """Mock the get_collection function to return a mock collection."""
    with patch('src.rag.analyzer.get_collection') as mock:
        # Create a mock collection
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'documents': [['This is a mock definition for the beat.']],
            'metadatas': [{'source': 'mock_source'}]
        }
        mock.return_value = mock_collection
        yield mock

def test_analyze_endpoint_success(mock_analyze_beat, sample_outline, sample_beat):
    """Test that the /analyze endpoint returns a successful response."""
    # Prepare the request payload
    payload = {
        "full_outline": sample_outline,
        "designated_beat": sample_beat,
        "beat_type": "Catalyst",
        "num_results": 3
    }
    
    # Send the request
    response = client.post("/analyze", json=payload)
    
    # Verify the response
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Verify the response structure
    assert "analysis" in data
    assert "flag" in data["analysis"]
    assert "explanation" in data["analysis"]
    assert "suggestions" in data["analysis"]
    
    # Verify the content matches our mock
    assert data["analysis"]["flag"] == "The Catalyst lacks sufficient emotional impact"
    assert data["analysis"]["explanation"] == "According to Save the Cat, the Catalyst should create a significant emotional reaction in the protagonist that forces them to consider change."
    assert len(data["analysis"]["suggestions"]) == 3
    assert data["analysis"]["suggestions"][0] == "Add more personal stakes to the letter - perhaps it mentions something from John's past"
    
    # Verify the mock was called with the correct arguments
    mock_analyze_beat.assert_called_once_with(
        outline=sample_outline,
        beat=sample_beat,
        beat_type="Catalyst"
    )

def test_analyze_endpoint_missing_fields():
    """Test that the /analyze endpoint returns an error for missing fields."""
    # Prepare an incomplete payload
    payload = {
        "full_outline": "Sample outline",
        # Missing designated_beat
        "beat_type": "Catalyst"
    }
    
    # Send the request
    response = client.post("/analyze", json=payload)
    
    # Verify the response
    assert response.status_code == 422  # Validation error

def test_analyze_endpoint_invalid_beat_type(mock_get_collection, mock_analyze_beat):
    """Test that the /analyze endpoint handles invalid beat types."""
    # Prepare a payload with an invalid beat type
    payload = {
        "full_outline": "Sample outline",
        "designated_beat": "Sample beat",
        "beat_type": "InvalidBeatType",
        "num_results": 3
    }
    
    # Send the request
    response = client.post("/analyze", json=payload)
    
    # Verify the response
    assert response.status_code == 200  # The API accepts any beat type string
    
    # Parse the response
    data = response.json()
    
    # Verify the response structure
    assert "analysis" in data
    assert "flag" in data["analysis"]
    assert "explanation" in data["analysis"]
    assert "suggestions" in data["analysis"]
    
    # Verify the mock was called with the correct arguments
    mock_analyze_beat.assert_called_once_with(
        outline="Sample outline",
        beat="Sample beat",
        beat_type="InvalidBeatType"
    )

def test_analyze_endpoint_error_handling(mock_analyze_beat):
    """Test that the /analyze endpoint handles errors gracefully."""
    # Make the mock raise an exception
    mock_analyze_beat.side_effect = Exception("Test error")
    
    # Prepare the request payload
    payload = {
        "full_outline": "Sample outline",
        "designated_beat": "Sample beat",
        "beat_type": "Catalyst",
        "num_results": 3
    }
    
    # Send the request
    response = client.post("/analyze", json=payload)
    
    # Verify the response
    assert response.status_code == 500
    
    # Parse the response
    data = response.json()
    
    # Verify the error message
    assert "detail" in data
    assert "Test error" in data["detail"] 