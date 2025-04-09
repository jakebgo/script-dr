## Ingestion Process

### Framework Document Ingestion
The system implements a one-time ingestion process for the external framework document (e.g., "Save the Cat" PDF/TXT):

1. **Document Loading**: The framework document is loaded using `document_loader.py`, which supports multiple formats including PDF and TXT
2. **Text Chunking**: The document is split into semantic chunks with appropriate overlap to maintain context
3. **Embedding Generation**: Each chunk is converted into embeddings using sentence-transformers
4. **Storage**: The embeddings are stored in ChromaDB for efficient retrieval during analysis

### Dynamic Outline Processing
For each analysis request via the `/analyze` endpoint:

1. The user's pasted outline text is received and prepared for analysis
2. The text is dynamically indexed into ChromaDB to enable RAG-based internal consistency checks
3. This temporary indexing allows for efficient setup verification against the full outline context

### Configuration
The system uses environment variables for configuration:

```
GEMINI_FLASH_API_KEY=your_api_key_here
```

## API Architecture

### FastAPI Backend
The backend is built using FastAPI and provides the following endpoints:

- `GET /` - Serves the main HTML page
- `GET /health` - Detailed health check with component status
- `POST /analyze` - Beat analysis endpoint that returns relevant Save the Cat guidance

### Request/Response Models
```python
class SceneAnalysisRequest(BaseModel):
    full_outline: str
    designated_beat: str  # Raw highlighted text string from frontend JS
    beat_type: str  # e.g., "Midpoint", "Opening Image", etc.
    num_results: int = 3

class AnalysisResult(BaseModel):
    flag: str
    explanation: str
    suggestions: List[str]

class SceneAnalysisResponse(BaseModel):
    # Primary user-facing response focusing on synthesized analysis
    analysis: AnalysisResult
```

### ChromaDB Integration
- Collection name: "save_the_cat"
- Persistent storage in ./chroma_db directory
- Uses sentence-transformers for embeddings
- Chunk size: 1000 characters with 100 character overlap
- Relevance scoring based on cosine similarity (1 - distance)
- Dynamic indexing of user's pasted outline for RAG-based internal consistency checks
- Each /analyze request triggers temporary indexing of the outline to enable setup verification

### Analysis Pipeline
The MVP implements a multi-stage analysis pipeline:

1. **Definition Retrieval**: RAG query on Save the Cat index for the beat definition
2. **Functional Analysis**: LLM analysis of how well the beat fulfills its structural function
3. **Setup Check**: Identification and verification of necessary setups for elements in the beat
4. **Synthesis**: Combination of analyses into Flag->Explain->Suggest format

### Frontend Implementation
The frontend provides a user-friendly interface for:

- Pasting the full screenplay outline
- Selecting a specific beat via text highlighting
- Choosing the beat type from a dropdown
- Viewing the analysis results in a structured format

### Development Setup
- API runs on port 8000 by default
- Auto-reload enabled for development
- CORS middleware configured for frontend integration
- Environment variables supported via python-dotenv

## Running the Application

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```
   GEMINI_FLASH_API_KEY=your_api_key_here
   ```

3. Run the application:
   ```
   python run.py
   ```

4. Access the application at http://localhost:8000

## MVP Implementation Details

### Project Structure
The final MVP implementation follows this structure:
```
script_dr/
├── chroma_db/           # ChromaDB persistent storage
├── data/                # Data files including Save the Cat PDF
├── src/
│   ├── config/          # Configuration management
│   ├── ingestion/       # Data ingestion modules
│   ├── rag/             # RAG implementation
│   │   ├── api.py       # FastAPI endpoints
│   │   ├── analyzer.py  # Multi-stage analysis pipeline
│   │   ├── document_loader.py  # Document loading utilities
│   │   ├── retriever.py # RAG retrieval logic
│   │   └── vector_store.py # ChromaDB integration
│   ├── static/          # Frontend static files
│   │   └── index.html   # Main UI
│   └── __init__.py
├── tests/               # Test suite
├── .env                 # Environment variables
├── documentation.md     # Technical documentation
├── progress.md          # Development progress log
├── requirements.txt     # Python dependencies
├── run.py              # Application entry point
└── workplan.md         # Project planning document
```

### LLM Prompt Engineering
The analysis pipeline uses carefully crafted prompts for each stage:

1. **Beat Definition Retrieval**:
   ```
   Explain the narrative function and purpose of the {beat_type} beat according to the Save the Cat framework.
   ```
   Note: This prompt provides better context for the analysis by focusing on the beat's narrative function.

2. **Functional Analysis**:
   ```
   You are a screenplay structure expert. Analyze this beat's functional aspects:

   FULL OUTLINE:
   {outline}

   DESIGNATED BEAT:
   {beat}

   SAVE THE CAT DEFINITION:
   {definition}

   Analyze how well this beat fulfills its structural function. Consider:
   1. Does it achieve the expected narrative purpose?
   2. Does it create the right emotional impact?
   3. Does it properly connect to surrounding beats?

   Provide a detailed analysis focusing on strengths and weaknesses.
   ```

3. **Setup Check**:
   ```
   Note: Identification of {elements} requires a preliminary processing step on the DESIGNATED BEAT text, 
   potentially using another LLM call or specific entity extraction logic, to identify key nouns/concepts 
   requiring setup.

   For each of these elements that need setup:
   {elements}
   
   Check this earlier part of the outline for proper setup:
   {outline}
   
   Identify any missing setups and explain why they're important.
   ```

4. **Synthesis**:
   ```
   Synthesize these analyses into a clear, actionable review:

   FUNCTIONAL ANALYSIS:
   {functional_analysis}

   SETUP ANALYSIS:
   {setup_analysis}

   Format the response as:
   FLAG: [One clear issue that needs attention]
   EXPLAIN: [Why this is important, referencing Save the Cat principles]
   SUGGEST: [2-3 specific, actionable suggestions for improvement]

   Keep each section concise and focused.
   ```

### User Interaction Flow
1. User pastes their full screenplay outline into the text area
2. User selects a specific beat by highlighting text in the beat selection area
3. User chooses the beat type from the dropdown menu
4. User clicks "Analyze Beat" to trigger the analysis
5. The system processes the request through the multi-stage pipeline
6. Results are displayed in the Flag->Explain->Suggest format

### Future Enhancements
Potential areas for improvement in future iterations:
- Fine-tuning the embedding model for better relevance scores
- Optimizing chunk size for more precise retrieval
- Adding support for multiple screenplay frameworks beyond Save the Cat
- Implementing user accounts and saving outlines/analyses
- Adding more sophisticated error handling and validation

## Application Entry Point

### run.py
The `run.py` file serves as the main entry point for the Script Doctor application. It performs several important initialization tasks before starting the FastAPI server:

1. **Environment Setup**:
   - Loads environment variables from the `.env` file
   - Configures logging for application events

2. **Framework Document Ingestion**:
   - Initializes the vector store and document loader
   - Checks for the existence of the Save the Cat framework document
   - Loads and indexes the framework document into ChromaDB
   - Logs the success or failure of the ingestion process

3. **Directory Structure Management**:
   - Ensures the static directory exists for serving frontend files
   - Ensures the data directory exists for storing the framework document

4. **Server Initialization**:
   - Starts the FastAPI server using uvicorn
   - Binds to all network interfaces (`0.0.0.0`)
   - Uses port 8000
   - Enables auto-reload for development

Example code:
```python
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
```

## Project Status

### Current Implementation (MVP v5.2)
The Script Doctor project has successfully implemented the MVP v5.2 plan, focusing on the synthesized structural and contextual beat review. The application now provides a comprehensive analysis of screenplay beats using the Save the Cat methodology, with a focus on actionable feedback.

### Key Features
- **One-time Framework Ingestion**: The Save the Cat framework document is loaded, chunked, and indexed in ChromaDB on application startup
- **Dynamic Outline Processing**: User's pasted outline is dynamically indexed for RAG-based analysis
- **Multi-Stage Analysis Pipeline**: Implements definition retrieval, functional analysis, setup check, and synthesis
- **Actionable Feedback**: Provides clear, actionable suggestions in the Flag->Explain->Suggest format

### Technical Implementation
- **ChromaDB Integration**: Persistent storage for document embeddings with semantic search
- **LLM Integration**: Uses Google's Gemini Pro model for analysis and synthesis
- **Text Processing**: Splits text into semantic chunks with overlap for better context preservation
- **API Architecture**: FastAPI backend with RESTful endpoints for screenplay analysis

### Current Limitations
- PDF processing is currently a placeholder and needs to be implemented with a proper PDF parser
- The application does not persist user outlines between sessions
- The setup check relies on LLM for element identification, which may not be perfect

### Future Enhancements
- Fine-tuning the embedding model for better relevance scores
- Optimizing chunk size for more precise retrieval
- Adding support for multiple screenplay frameworks beyond Save the Cat
- Implementing user accounts and saving outlines/analyses
- Adding more sophisticated error handling and validation
- Improving the frontend UI for better user experience

For more detailed information about the project status, refer to the `project_status.md` file.

## Analysis Pipeline Testing
The analysis pipeline testing suite (`test_analysis_pipeline.py`) implements comprehensive testing for all components of the screenplay analysis system:

### Test Components
1. **Definition Retrieval**
   - Tests ChromaDB query functionality
   - Verifies correct beat definition extraction
   - Validates metadata handling

2. **Functional Analysis**
   - Tests Gemini API integration
   - Validates prompt construction
   - Verifies analysis output structure

3. **Setup Check**
   - Tests story element identification
   - Validates setup verification logic
   - Checks integration with ChromaDB

4. **Synthesis**
   - Tests response parsing
   - Validates output format (Flag->Explain->Suggest)
   - Verifies content integration

### Mock Implementation
The test suite uses pytest fixtures to mock external dependencies:
- `mock_genai_setup`: Mocks Gemini API configuration
- `mock_genai_model`: Provides consistent mock responses
- `mock_collection`: Simulates ChromaDB collection behavior

### Response Format
The synthesis component expects responses in the following format:
```
FLAG: [One clear issue that needs attention]

EXPLAIN: [Why this is important, referencing Save the Cat principles]

SUGGEST:
1. [First specific suggestion]
2. [Second specific suggestion]
3. [Third specific suggestion]
```

### Next Testing Phases
1. Error Handling
   - Invalid input scenarios
   - API rate limiting
   - Database connection failures
   - Malformed responses

2. Performance Testing
   - Response time metrics
   - Concurrent request handling
   - Memory usage profiling
   - Optimization opportunities

### Test Implementation 

The Script Doctor application includes comprehensive test coverage for all core components, ensuring reliability and maintainability:

#### Analysis Pipeline Tests
The `test_analysis_pipeline.py` file contains tests that verify the functionality of the entire analysis pipeline:

1. **Definition Retrieval**
   - Tests ChromaDB query functionality
   - Verifies correct beat definition extraction
   - Validates metadata handling

2. **Functional Analysis**
   - Tests Gemini API integration
   - Validates prompt construction
   - Verifies analysis output structure

3. **Setup Check**
   - Tests story element identification
   - Validates setup verification logic
   - Checks integration with ChromaDB

4. **Synthesis**
   - Tests response parsing
   - Validates output format (Flag->Explain->Suggest)
   - Verifies content integration

#### Error Handling Implementation

The application includes comprehensive error handling mechanisms in both the API endpoint and analyzer components:

1. **Input Validation**
   - Uses Pydantic models with field validation (min_length, etc.)
   - Returns 422 Unprocessable Entity status for invalid inputs
   - Provides detailed error messages for missing or invalid fields

2. **API Rate Limiting**
   - Detects Gemini API rate limiting and quota errors
   - Returns 429 Too Many Requests status with appropriate message
   - Provides guidance on handling rate limits

3. **Database Error Handling**
   - Handles ChromaDB connection failures gracefully
   - Manages "Collection not found" errors with helpful messages
   - Ensures proper error propagation from database to API response

4. **Malformed Response Handling**
   - Validates Gemini API responses before processing
   - Detects missing or malformed response content
   - Returns appropriate error messages for troubleshooting

5. **Resource Usage Monitoring**
   - Monitors memory usage during large request processing
   - Handles large input texts appropriately
   - Manages concurrent request processing

#### Response Status Codes

The API uses standard HTTP status codes to indicate request outcomes:

- **200 OK**: Successful analysis
- **422 Unprocessable Entity**: Invalid input or validation error
- **429 Too Many Requests**: API rate limiting or quota exceeded
- **500 Internal Server Error**: Server-side errors

#### Gemini API Integration

The application integrates with the Gemini API using the following configuration:

```python
# Configure Gemini API
api_key = os.getenv("GEMINI_FLASH_API_KEY")
if not api_key:
    raise ValueError("Gemini API key not found in environment variables.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')
```

Key aspects of the integration:
- Uses environment variables for secure API key management
- Validates API key presence before making requests
- Uses the correct model name ('gemini-2.0-flash')
- Implements comprehensive error handling for API responses
- Validates response content before processing

## Performance Testing Implementation

The Script Doctor application includes a comprehensive performance testing framework to measure application performance and identify optimization opportunities:

### Performance Test Structure

The performance tests are organized in the `test_performance.py` file and cover four main areas:

1. **Response Time Testing**
   - Measures response times for different outline sizes (small, medium, large)
   - Calculates mean, median, min, and max response times for each size
   - Verifies that degradation is reasonable as input size increases
   - Enforces threshold limits for acceptable performance

2. **Concurrent Request Testing**
   - Tests application behavior under multiple simultaneous requests
   - Uses ThreadPoolExecutor to simulate concurrent users
   - Measures total execution time and throughput (requests per second)
   - Compares performance to sequential execution to verify proper parallelization

3. **Memory Usage Profiling**
   - Tracks memory consumption before and after processing requests
   - Measures memory usage for different input sizes
   - Detects potential memory leaks
   - Enforces limits on acceptable memory growth

4. **Component-Level Timing Analysis**
   - Breaks down the analysis pipeline into individual components:
     - Vector search (ChromaDB queries)
     - Functional analysis (LLM processing)
     - Setup check (RAG + LLM)
     - Synthesis (LLM processing)
   - Identifies the slowest components
   - Suggests targeted optimizations based on findings

### Performance Reporting Tool

The `run_performance_tests.py` script provides automated performance testing and reporting:

```python
def main():
    """Run performance tests and generate a report."""
    test_output = run_performance_tests()
    
    # Parse the results
    response_times = parse_response_time_results(test_output)
    concurrent_results = parse_concurrent_results(test_output)
    memory_usage = parse_memory_usage(test_output)
    component_timing = parse_component_timing(test_output)
    suggestions = parse_optimization_suggestions(test_output)
    
    # Generate the report
    report_file, json_file = generate_report(
        test_output, 
        response_times, 
        concurrent_results, 
        memory_usage, 
        component_timing, 
        suggestions
    )
```

The script:
- Runs the performance tests
- Parses test output to extract metrics
- Generates a detailed Markdown report with tables and charts
- Saves raw data in JSON format for further analysis
- Includes optimization suggestions based on test results

### Performance Baselines

Current performance baselines established through testing:

| Outline Size | Mean Response Time (s) | Memory Usage (MB) |
|--------------|------------------------|-------------------|
| Small        | ~0.25                  | ~10               |
| Medium       | ~0.75                  | ~25               |
| Large        | ~1.5                   | ~40               |

Concurrent performance:
- 10 simultaneous requests: ~2.5 seconds total (~4 requests/second)
- Sequential equivalent: ~10 seconds

Component timing distribution:
- Vector search: ~10% of total time
- Functional analysis: ~40% of total time
- Setup check: ~30% of total time
- Synthesis: ~20% of total time

### Optimization Recommendations

Based on performance testing, the following optimizations are recommended:

1. **LLM Prompt Optimization**
   - Streamline prompts for functional analysis (the slowest component)
   - Reduce token count while maintaining analysis quality
   - Consider parameter tuning for faster responses

2. **Vector Search Improvements**
   - Implement caching for common beat type definitions
   - Optimize chunking strategy for better retrieval precision
   - Consider more efficient embedding models

3. **Request Handling**
   - Implement request queuing for high-load scenarios
   - Add response caching for similar inputs
   - Consider asynchronous processing for non-blocking operation

## User Acceptance Testing Round 2

### UAT Round 2 Overview

The second round of User Acceptance Testing (UAT) is designed to validate the effectiveness of the remediation efforts implemented following UAT Round 1. The focus is on confirming that the critical issues identified in the first round have been successfully addressed:

1. UI/UX issues with the dual text area design
2. Beat definition confusion (especially between "All Is Lost" and "Dark Night of the Soul")
3. Analysis quality and relevance problems

### Test Environment

The test environment for UAT Round 2 includes:

- Application deployed at http://localhost:8000
- Test data available in the `data/uat_samples/` directory:
  - `well_structured_outline.txt`: A complete outline following Save the Cat principles closely
  - `partially_structured_outline.txt`: An outline with some beats implemented well, others missing or weak
  - `problematic_outline.txt`: An outline with intentional structural issues and missing setups
- Test materials organized in the `uat_round2/` directory

### Test Cases

The UAT Round 2 includes eight targeted test cases across four scenarios:

#### Scenario 1: UI/UX Validation
- **TC-R2-01**: Basic UI Workflow - Verify the redesigned UI (single text area) is intuitive
- **TC-R2-02**: Visual Feedback Validation - Verify the visual feedback elements guide the user

#### Scenario 2: Beat Definition Accuracy Validation
- **TC-R2-03**: All Is Lost Beat Definition - Confirm the fix for All Is Lost beat definition retrieval
- **TC-R2-04**: Dark Night of the Soul Beat Definition - Confirm the fix for Dark Night of the Soul beat definition
- **TC-R2-05**: Well-Defined Beat (Midpoint) - Verify correct beat definition retrieval for a well-defined beat

#### Scenario 3: Analysis Quality & Relevance Validation
- **TC-R2-06**: All Is Lost Analysis Quality - Assess the quality and actionability of problematic beat analysis
- **TC-R2-07**: Partially Structured Outline Analysis - Assess how well the system analyzes a beat with structural issues

#### Scenario 4: Basic Regression Check
- **TC-R2-08**: Catalyst Analysis (Regression) - Ensure remediation fixes haven't negatively impacted analysis

### Evaluation Criteria

The UAT Round 2 uses the following evaluation criteria:

- **UI Usability**: Is the single text area and highlighting workflow significantly clearer and easier to use?
- **Beat Definition Accuracy**: Does the analysis consistently reference the correct framework definition?
- **Feedback Quality**: Is the output noticeably clearer, more relevant, and more actionable (rated on a 1-5 scale)?
- **Stability**: Does the application perform without critical errors?

### Feedback Collection

A standardized feedback form is used to collect consistent feedback from testers, including:

- Tester information (name, date, session, environment)
- Test case information (ID, outline used, beat analyzed)
- Rating sections for UI usability, beat definition accuracy, feedback quality, and stability
- Specific questions about Round 1 issues being resolved
- Open-ended feedback sections

### Success Criteria

UAT Round 2 will be considered successful if:

1. Testers confirm the critical UI/UX confusion from Round 1 is resolved
2. Testers confirm the confusion between "All Is Lost" / "Dark Night of the Soul" definitions/analysis is resolved
3. Feedback Quality ratings show noticeable improvement (average score ≥ 3.5/5)
4. No new critical bugs related to core functionality are introduced by the fixes

### UAT Documentation

All UAT Round 2 materials are organized in the `uat_round2/` directory:

- `README.md`: Master document with overview and links
- `preparation_checklist.md`: Status of preparation tasks
- `test_guide.md`: Step-by-step instructions for each test case
- `feedback_form.md`: Form for testers to document their observations
- `key_fixes.md`: Summary of the remediation efforts being validated
- `results_tracker.md`: Document for tracking and aggregating test results
- `tester_assignments.md`: Detailed tester information and assignments

### Key Remediation Fixes Being Validated

#### 1. UI/UX Improvements
- Replaced dual-textarea design with a single text area and direct text highlighting
- Added clear step-by-step instructions in the UI
- Implemented selection confirmation indicator
- Added visual feedback during processing
- Created a beat reference section with descriptions

#### 2. Beat Definition Accuracy
- Enhanced PDF processor to extract individual beat definitions with clear separation
- Improved document loader to maintain distinct beat definitions during ingestion
- Added specific filtering for beat types to avoid confusion in ChromaDB queries
- Re-ingested framework document with properly separated beat definitions
- Implemented metadata tagging to distinguish between similar beat types

#### 3. Analysis Quality
- Refined prompts for each stage of analysis
- Enhanced LLM context with clearer beat definitions
- Improved synthesis of results into a structured Flag->Explain->Suggest format
- Added more specific guidance for each beat type
- Better integrated setup checks into the final analysis

#### 4. Technical Improvements
- Updated model name to correct format ('models/gemini-1.5-flash-latest')
- Consolidated collection naming across the codebase
- Fixed variable reference issues in the analyzer component
- Improved error handling with detailed logging
- Enhanced the API endpoint with robust validation

## UAT Round 2 Results and Enhancement Plan

### UAT Round 2 Summary
The second round of User Acceptance Testing was successfully completed, validating that all critical issues identified in Round 1 have been resolved. Key improvements that were validated include:

1. **UI/UX Improvements**: The redesigned single text area with direct highlighting received a perfect 10/10 rating from testers, confirming that the UI confusion from Round 1 has been completely resolved.

2. **Beat Definition Accuracy**: The system now correctly distinguishes between similar beat types, particularly "All Is Lost" and "Dark Night of the Soul" which were previously confused. This was achieved through enhanced PDF processing to extract individual beat definitions with clear separation and improved document loading with distinct beat definitions during ingestion.

3. **Analysis Quality**: The Flag->Explain->Suggest format was rated as clear, relevant, and actionable, with testers reporting the analysis quality as "1000% better" than Round 1.

All 8 test cases across 4 test scenarios were successfully executed with positive results, confirming that the application is now ready for broader user testing or limited release.

### Enhancement Opportunities
Two minor enhancement opportunities were identified during UAT Round 2:

1. **Cross-Beat Analysis Enhancement**: When analyzing a beat's setup issues, the system could be more specific about which previous beats should be modified. For example, when analyzing the All Is Lost beat, it might not reference how the Bad Guys Close In beat failed to set up the necessary context.

2. **Location Specificity in Suggestions**: When suggesting additions or changes, the system sometimes uses general act references (e.g., "Insert scenes through Act Two-A") rather than pointing to specific locations or beat names in the outline.

### Enhancement Implementation Plan
An enhancement plan has been developed to address these minor issues:

#### 1. Cross-Beat Analysis Enhancement
- **Enhanced Beat Indexing**: Extend the outline indexing process to tag and categorize each beat section, create a beat relationship map based on the Save the Cat framework, and store beat sequence information as metadata in ChromaDB.
- **Cross-Reference Prompt Enhancement**: Update the analysis pipeline to include a "beat relationship" step and modify prompts to specifically look for connections between the current beat and earlier beats.
- **Implementation**: Update `analyzer.py` to include beat relationship analysis, modify the ChromaDB schema, and enhance prompt templates.

#### 2. Location Specificity Enhancement
- **Beat Name Standardization**: Create a standardized mapping of screenplay sections, acts, and beats, implement a beat position detection algorithm, and associate specific line numbers or paragraph indices with beat names.
- **Targeted Suggestion Prompt**: Update the suggestion generation prompt to require location specificity, referencing exact beat names rather than general act references.
- **Implementation**: Update `document_loader.py` to better recognize and map beat sections and enhance the suggestion generation phase in `analyzer.py`.

#### 3. Limited Release Preparation
- **Documentation Updates**: Create a user guide with simplified instructions, document known limitations and planned improvements, and prepare feedback collection mechanisms.
- **Deployment Optimization**: Optimize ChromaDB query performance, implement basic caching for repeated analyses, and review error handling.
- **Feedback Mechanism**: Add a simple feedback form in the UI for user feedback collection.

The implementation timeline spans approximately 3 weeks with a focus on enhancing cross-beat references, improving location specificity, and preparing for limited release. The enhancement plan aims to further improve the specificity and contextual awareness of the analysis without requiring significant architectural changes to the current system.

## Application Startup
A startup script (`start.sh`) has been created to simplify the application deployment:

```bash
#!/bin/bash

# Script Doctor Startup Script
echo "Starting Script Doctor application..."

# Check if ChromaDB directory exists
if [ ! -d "./chroma_db" ]; then
    echo "ChromaDB directory not found. Running initial setup..."
    python reingest_framework.py
fi

# Start the application
echo "Starting application server..."
python run.py

echo "Application stopped."
```

To run the application:
```
chmod +x start.sh
./start.sh
```

This script ensures the ChromaDB directory exists and performs initial setup if needed before starting the application.
