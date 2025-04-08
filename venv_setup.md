# Virtual Environment Setup Guide

This document provides instructions for setting up the virtual environment required for the Script Doctor project.

## Prerequisites
- Python 3.13.2 installed (project was developed with this version)
- pip (Python package installer)

## Setup Instructions

### 1. Create a new virtual environment

**For macOS/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**For Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

#### Option 1: Minimal requirements (recommended for development)
```bash
pip install -r requirements.txt
```

#### Option 2: Full environment with exact versions
For an exact replica of the development environment:
```bash
pip install -r requirements-full.txt
```

### 3. Verify installation
You can verify the installation by running:
```bash
python -c "import chromadb, pandas, numpy, PyPDF2; print('Setup successful!')"
```

## Environment Variables

Create a `.env` file in the project root with the following variables:
```
DB_PATH=./chroma_db
PDF_PATH=./data/save_the_cat.pdf
GOOGLE_API_KEY=your_google_api_key  # If using Google Generative AI
```

## Running the application
```bash
python run.py
```

Or to start the API server:
```bash
python src/run_api.py
```

## Notes
- The ChromaDB vector store data is stored in the `chroma_db` directory, which is excluded from Git
- Output files are stored in the `output` directory, also excluded from Git
- Logs are stored in text files with the `.txt` extension and are excluded from Git 