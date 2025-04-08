# Script Doctor

A screenplay analysis tool that uses the Save the Cat methodology to provide structural feedback on your screenplay beats.

## Features

- **Beat Analysis**: Analyze specific beats in your screenplay using the Save the Cat framework
- **Setup Verification**: Check for proper setup of story elements
- **Actionable Feedback**: Receive clear, actionable suggestions for improvement
- **RAG-Based Analysis**: Uses Retrieval-Augmented Generation for accurate framework guidance

## Project Structure

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

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:
```
GEMINI_FLASH_API_KEY=your_api_key_here
```

4. Place your Save the Cat framework document in the `data` directory:
```
data/save_the_cat.pdf
```

## Usage

1. Run the application:
```bash
python run.py
```

2. Access the application at http://localhost:8000

3. Paste your screenplay outline and select a beat to analyze

## How It Works

1. **Framework Document Ingestion**: The Save the Cat framework document is loaded, chunked, and indexed in ChromaDB
2. **Dynamic Outline Processing**: Your pasted outline is dynamically indexed for RAG-based analysis
3. **Multi-Stage Analysis**:
   - Definition Retrieval: Get the Save the Cat definition for the beat
   - Functional Analysis: Analyze how well the beat fulfills its structural function
   - Setup Check: Verify proper setup of story elements
   - Synthesis: Combine analyses into actionable feedback

## Development

- API runs on port 8000 by default
- Auto-reload enabled for development
- CORS middleware configured for frontend integration
- Environment variables supported via python-dotenv 