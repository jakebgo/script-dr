import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil
import os

from src.ingestion.day1_ingestion import Day1Ingestion
from src.config.config import Config

@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame({
        'timestamp': ['2024-01-01 00:00:00', '2024-01-01 00:01:00'],
        'value': [1.0, 2.0],
        'source': ['test1', 'test2'],
        'metadata': ['{"key": "value1"}', '{"key": "value2"}']
    })

def test_validate_dataframe(sample_data):
    """Test dataframe validation."""
    ingestion = Day1Ingestion()
    assert ingestion.validate_dataframe(sample_data, ingestion.required_columns)
    
    # Test with missing columns
    invalid_df = sample_data.drop(columns=['timestamp'])
    assert not ingestion.validate_dataframe(invalid_df, ingestion.required_columns)

def test_transform_data(sample_data):
    """Test data transformation."""
    ingestion = Day1Ingestion()
    transformed_df = ingestion.transform_data(sample_data)
    
    assert isinstance(transformed_df['timestamp'].iloc[0], pd.Timestamp)
    assert isinstance(transformed_df['value'].iloc[0], float)
    assert isinstance(transformed_df['metadata'].iloc[0], dict)

def test_process_file(temp_data_dir, sample_data):
    """Test file processing."""
    # Set up test environment
    Config.DATA_SOURCE_PATH = temp_data_dir
    Config.OUTPUT_PATH = temp_data_dir
    
    # Create test file
    test_file = Path(temp_data_dir) / 'test.csv'
    sample_data.to_csv(test_file, index=False)
    
    # Run ingestion
    ingestion = Day1Ingestion()
    result = ingestion.process_file(test_file)
    
    assert result
    assert (Path(temp_data_dir) / f'processed_{test_file.name}').exists()

def test_run_empty_directory(temp_data_dir):
    """Test running ingestion with empty directory."""
    Config.DATA_SOURCE_PATH = temp_data_dir
    Config.OUTPUT_PATH = temp_data_dir
    
    ingestion = Day1Ingestion()
    ingestion.run()  # Should not raise any errors 