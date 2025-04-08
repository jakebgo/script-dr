# Script Doctor - Testing Documentation

This document provides comprehensive guidance for running and maintaining the Script Doctor test suite.

## Test Structure

The Script Doctor test suite is organized into the following categories:

1. **Unit Tests**
   - `test_save_the_cat_ingestion.py`: Tests for framework document ingestion and RAG retrieval.
   - `test_day1_ingestion.py`: Tests for the Day 1 ingestion pipeline.

2. **Integration Tests**
   - `test_analyze_endpoint.py`: Tests for the `/analyze` API endpoint.
   - `test_analysis_pipeline.py`: Tests for the complete analysis pipeline.

3. **Error Handling Tests**
   - `test_error_handling.py`: Tests for error handling in various scenarios.

4. **Performance Tests**
   - `test_performance.py`: Tests for application performance metrics.

## Running Tests

### Prerequisites

- Python 3.10+
- All dependencies installed (`pip install -r requirements.txt`)
- Environment variables set in `.env` file:
  ```
  GEMINI_FLASH_API_KEY=your_api_key_here
  ```

### Running All Tests

To run the entire test suite:

```bash
pytest
```

### Running Specific Test Categories

To run tests from a specific file:

```bash
pytest tests/test_save_the_cat_ingestion.py
```

To run tests matching a specific pattern:

```bash
pytest -k "ingestion"  # Runs all tests with "ingestion" in the name
```

### Running Tests with Output Verbosity

For detailed test output:

```bash
pytest -v
```

For even more detailed output:

```bash
pytest -vv
```

### Running Tests with Coverage Report

To generate a test coverage report:

```bash
pytest --cov=src tests/
```

For an HTML coverage report:

```bash
pytest --cov=src --cov-report=html tests/
```

## Test Fixtures

The test suite uses several fixtures to set up test environments and mock external dependencies:

1. **Data Fixtures**
   - `sample_outline`: Provides a sample screenplay outline for testing.
   - `sample_beat`: Provides a sample designated beat for testing.
   - `sample_outlines`: Provides outlines of different sizes for performance testing.

2. **Mock Fixtures**
   - `mock_genai_setup`: Mocks the Gemini API configuration.
   - `mock_genai_model`: Provides consistent mock responses for Gemini API.
   - `mock_collection`: Simulates ChromaDB collection behavior.
   - `mock_vector_store`: Mocks the VectorStore with a proper collection.
   - `mock_analyze_beat`: Mocks the analyze_beat function for testing.

3. **Environment Fixtures**
   - `temp_data_dir`: Creates a temporary directory for test data.
   - `temp_chroma_dir`: Creates a temporary directory for ChromaDB.

## Mocking External Dependencies

The test suite mocks external dependencies to avoid network calls and ensure consistent behavior:

### Mocking Gemini API

```python
@pytest.fixture(autouse=True)
def mock_genai_setup():
    """Mock the Gemini API setup and configuration."""
    with patch('google.generativeai.configure') as mock_configure:
        yield mock_configure

@pytest.fixture
def mock_genai_model():
    """Mock the Gemini GenerativeModel for testing."""
    with patch('google.generativeai.GenerativeModel') as mock_model:
        instance = mock_model.return_value
        content_mock = MagicMock()
        content_mock.text = "Mocked GenerativeModel response"
        instance.generate_content.return_value = content_mock
        yield instance
```

### Mocking ChromaDB

```python
@pytest.fixture
def mock_collection():
    """Mock ChromaDB collection."""
    mock = MagicMock()
    mock.query.return_value = {
        'documents': [['The Catalyst is a life-changing moment.']],
        'metadatas': [{'source': 'save_the_cat_beats.json'}]
    }
    return mock
```

## Performance Testing

The performance tests are designed to measure several key metrics:

1. **Response Time**
   - Tests response times for different outline sizes (small, medium, large).
   - Calculates mean, median, min, and max response times.
   - Ensures degradation is reasonable as input size increases.

2. **Concurrent Requests**
   - Tests how the application handles multiple simultaneous requests.
   - Measures total execution time for a set of concurrent requests.
   - Compares performance to sequential execution to ensure proper parallelization.

3. **Memory Usage**
   - Profiles memory consumption during analysis of different size outlines.
   - Identifies potential memory leaks.
   - Establishes baseline memory requirements.

4. **Component Timing**
   - Measures execution time for each component of the analysis pipeline.
   - Identifies bottlenecks in the processing pipeline.
   - Suggests optimization opportunities based on the slowest components.

## Interpreting Test Results

### Success Criteria

All tests should pass with the following results:

- **Unit Tests**: Verify individual components work correctly.
- **Integration Tests**: Confirm components work together properly.
- **Error Handling Tests**: Ensure the application handles errors gracefully.
- **Performance Tests**: Establish performance baselines.

### Performance Test Thresholds

The performance tests include thresholds for acceptable performance:

- **Response Time**: Large outline analysis should be < 2.0 seconds.
- **Concurrent Requests**: Performance should be better than sequential execution.
- **Memory Usage**: Memory increase for large outlines should be < 50MB.

### Optimization Recommendations

The performance tests suggest optimizations based on the identified bottlenecks:

- **Vector Search**: Optimize indexing, implement caching.
- **Functional Analysis**: Optimize LLM prompts, consider using faster models.
- **Setup Check**: Improve verification algorithm, implement selective checking.
- **Synthesis**: Simplify prompts, use template-based responses for common issues.

## Continuous Integration

The test suite is designed to be run in a CI/CD pipeline. To integrate with CI/CD:

1. Install dependencies:
   ```yaml
   - name: Install dependencies
     run: pip install -r requirements.txt
   ```

2. Run tests:
   ```yaml
   - name: Run tests
     run: pytest
   ```

3. Generate coverage reports:
   ```yaml
   - name: Generate coverage report
     run: pytest --cov=src --cov-report=xml
   ``` 