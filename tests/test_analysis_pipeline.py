import pytest
from unittest.mock import patch, MagicMock
import os
import tempfile
import shutil
import google.generativeai as genai

from src.rag.analyzer import (
    analyze_beat,
    get_beat_definition,
    analyze_functional_aspects,
    check_setups,
    synthesize_analysis,
    index_outline
)

@pytest.fixture(autouse=True)
def mock_genai_setup():
    """Mock the Gemini API setup and configuration."""
    with patch('google.generativeai.configure') as mock_configure:
        yield mock_configure

@pytest.fixture(autouse=True)
def mock_genai_model():
    """Mock the Gemini Pro model responses."""
    mock_response = MagicMock()
    mock_response.text = """FLAG: The Catalyst needs stronger emotional resonance and better setup.

EXPLAIN: The Save the Cat framework emphasizes that the Catalyst should not only present an opportunity but also create a strong emotional reaction that forces the protagonist to consider change.

SUGGEST:
1. Add earlier hints about the adventure club through background elements
2. Establish the protagonist's financial situation in the Set-Up
3. Create more emotional impact by connecting the letter to the protagonist's established dreams"""
    
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    
    with patch('src.rag.analyzer.model', mock_model):
        yield mock_model

@pytest.fixture
def mock_collection():
    """Create a mock ChromaDB collection."""
    mock = MagicMock()
    mock.query.return_value = {
        'documents': [['The Catalyst (also known as the Inciting Incident) is a life-changing moment that disrupts the protagonist\'s status quo and forces them to consider change. This beat should create significant emotional impact and clearly establish what\'s at stake.']],
        'metadatas': [{'source': 'save_the_cat.pdf', 'page': 1}]
    }
    return mock

@pytest.fixture
def sample_outline():
    """Sample screenplay outline for testing."""
    return """
    ACT ONE
    
    OPENING IMAGE: John Smith, a middle-aged accountant, sits alone in his cubicle, surrounded by paperwork.
    
    THEME STATED: His boss tells him "Life is about taking risks, not playing it safe."
    
    SET-UP: We see John's daily routine - same route to work, same lunch, empty apartment.
    
    CATALYST: John receives a mysterious letter inviting him to join an exclusive adventure club.
    
    DEBATE: John researches the club and debates whether to join.
    """

@pytest.fixture
def sample_beat():
    """Sample beat for testing."""
    return "John receives a mysterious letter inviting him to join an exclusive adventure club."

def test_get_beat_definition(mock_collection):
    """Test retrieving beat definitions from ChromaDB."""
    definition = get_beat_definition("Catalyst", mock_collection)
    
    # Verify the definition was retrieved
    assert definition is not None
    assert "Catalyst" in definition
    assert "Inciting Incident" in definition
    
    # Verify the collection was queried correctly
    mock_collection.query.assert_called_once()
    query_args = mock_collection.query.call_args[1]
    assert "Catalyst" in query_args['query_texts'][0]
    assert query_args['n_results'] == 1

def test_analyze_functional_aspects(mock_genai_model, sample_outline, sample_beat):
    """Test the functional analysis of a beat."""
    # Analyze the beat
    analysis = analyze_functional_aspects(
        outline=sample_outline,
        beat=sample_beat,
        definition="The Catalyst should create significant emotional impact."
    )
    
    # Verify the analysis content
    assert analysis is not None
    assert len(analysis) > 0
    
    # Verify the model was called with correct prompt
    mock_genai_model.generate_content.assert_called_once()
    prompt = mock_genai_model.generate_content.call_args[0][0]
    assert "FULL OUTLINE" in prompt
    assert "DESIGNATED BEAT" in prompt
    assert "SAVE THE CAT DEFINITION" in prompt

def test_check_setups(mock_genai_model, mock_collection, sample_outline, sample_beat):
    """Test checking for proper setups of story elements."""
    # Check setups
    setup_analysis = check_setups(
        outline=sample_outline,
        beat=sample_beat,
        collection=mock_collection
    )
    
    # Verify the setup analysis content
    assert setup_analysis is not None
    assert len(setup_analysis) > 0
    
    # Verify the model was called
    assert mock_genai_model.generate_content.called

def test_synthesize_analysis(mock_genai_model):
    """Test synthesizing the analyses into a final result."""
    # Prepare test inputs
    functional_analysis = "The beat effectively establishes the catalyst moment but needs stronger emotional impact."
    setup_analysis = "The adventure club and financial stakes need better setup."
    
    # Synthesize the analysis
    result = synthesize_analysis(functional_analysis, setup_analysis)
    
    # Verify the result structure
    assert "flag" in result
    assert "explanation" in result
    assert "suggestions" in result
    
    # Verify the model was called with correct prompt
    mock_genai_model.generate_content.assert_called()
    prompt = mock_genai_model.generate_content.call_args[0][0]
    assert "FUNCTIONAL ANALYSIS" in prompt
    assert "SETUP ANALYSIS" in prompt
    assert "Format the response as:" in prompt

def test_full_analysis_pipeline(mock_genai_model, mock_collection, sample_outline, sample_beat):
    """Test the complete analysis pipeline end-to-end."""
    # Mock the get_collection function
    with patch('src.rag.analyzer.get_collection', return_value=mock_collection):
        # Run the full analysis
        result = analyze_beat(
            outline=sample_outline,
            beat=sample_beat,
            beat_type="Catalyst"
        )
        
        # Verify the result structure
        assert "flag" in result
        assert "explanation" in result
        assert "suggestions" in result
        
        # Verify each stage was executed
        assert mock_genai_model.generate_content.call_count >= 3  # Called for each stage
        
        # Verify the content integration
        assert result["flag"]  # Should not be empty
        assert "Save the Cat" in result["explanation"]
        assert len(result["suggestions"]) >= 1

def test_index_outline():
    """Test the dynamic indexing of outlines."""
    # Create a temporary directory for ChromaDB
    with tempfile.TemporaryDirectory() as temp_dir:
        # Index the outline
        outline = "Test outline content"
        collection_name = index_outline(outline)
        
        # Verify the collection name format
        assert collection_name.startswith("outline_")
        assert len(collection_name) > len("outline_")  # Should include a UUID
        
        # Clean up
        shutil.rmtree(temp_dir) 