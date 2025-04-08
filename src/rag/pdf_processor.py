import os
import sys
from PyPDF2 import PdfReader
import json
from pathlib import Path
import re
import chromadb
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        logging.info(f"Total pages in PDF: {len(reader.pages)}")
        
        text = ""
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                logging.info(f"Processing page {i+1}/{len(reader.pages)} - Extracted {len(page_text)} characters")
                text += page_text + "\n"
            except Exception as e:
                logging.error(f"Error processing page {i+1}: {str(e)}")
        
        logging.info(f"Total text extracted: {len(text)} characters")
        return text
    except Exception as e:
        logging.error(f"Error opening PDF {pdf_path}: {str(e)}")
        raise

def clean_text(text):
    """Clean and normalize text."""
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove multiple newlines
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()

def extract_beats(text):
    """
    Extract individual beat definitions from the Save the Cat framework document.
    This function attempts to identify each beat type and its description separately.
    """
    logging.info("Extracting beat definitions from text...")
    
    # Common beat types from Save the Cat
    beat_types = [
        "Opening Image", "Theme Stated", "Setup", "Catalyst", "Debate",
        "Break Into Two", "B Story", "Fun and Games", "Midpoint",
        "Bad Guys Close In", "All Is Lost", "Dark Night of the Soul",
        "Break Into Three", "Finale", "Final Image"
    ]
    
    # Create a regex pattern to find sections that likely contain beat definitions
    # This pattern looks for sections that start with a beat type name
    beat_pattern = r'(' + '|'.join(re.escape(beat) for beat in beat_types) + r')\s*[\.\:\-]?\s*(.+?)(?=(' + '|'.join(re.escape(beat) for beat in beat_types) + r')\s*[\.\:\-]|\Z)'
    
    # Find all matches using regex
    matches = re.finditer(beat_pattern, text, re.DOTALL)
    
    beat_documents = []
    for match in matches:
        beat_type = match.group(1).strip()
        description = match.group(2).strip()
        
        # Clean up the description
        description = re.sub(r'\s+', ' ', description)
        
        # Create a structured document for this beat
        beat_doc = f"BEAT TYPE: {beat_type}\n\nDEFINITION: {description}\n\nThis is the '{beat_type}' beat according to the Save the Cat screenplay structure framework."
        
        beat_documents.append({
            "type": beat_type,
            "text": beat_doc
        })
        
        logging.info(f"Extracted beat: {beat_type} ({len(description)} chars)")
    
    logging.info(f"Total beats extracted: {len(beat_documents)}")
    return beat_documents

def process_document(text):
    """Process the document text to extract beat definitions."""
    # Clean the text
    logging.info("Cleaning text...")
    text = clean_text(text)
    logging.info(f"Text length after cleaning: {len(text)} characters")
    
    # Extract individual beat definitions
    beat_documents = extract_beats(text)
    
    if not beat_documents:
        logging.warning("No beat definitions extracted! Falling back to chunking method.")
        return chunk_text(text)
    
    # Return the processed beat documents
    return beat_documents

def chunk_text(text, chunk_size=1000, overlap=100):
    """
    Fallback method: Split text into overlapping chunks while preserving sentence integrity.
    """
    logging.info(f"Starting text chunking with chunk_size={chunk_size}, overlap={overlap}")
    
    # First split into sentences using common sentence endings
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    logging.info(f"Split text into {len(sentences)} sentences")
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for i, sentence in enumerate(sentences):
        sentence_length = len(sentence)
        
        # If adding this sentence would exceed chunk size, save current chunk and start new one
        if current_length + sentence_length > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            # Keep last few sentences for overlap
            overlap_sentences = []
            overlap_length = 0
            for s in reversed(current_chunk):
                if overlap_length + len(s) <= overlap:
                    overlap_sentences.insert(0, s)
                    overlap_length += len(s)
                else:
                    break
            current_chunk = overlap_sentences
            current_length = overlap_length
        
        current_chunk.append(sentence)
        current_length += sentence_length
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    # Convert to same format as beat_documents for consistency
    chunk_documents = []
    for i, chunk in enumerate(chunks):
        chunk_documents.append({"type": "chunk", "text": chunk})
    
    return chunk_documents

def setup_chromadb():
    """Initialize ChromaDB."""
    logging.info("Setting up ChromaDB...")
    try:
        # Create client and collection
        logging.info("Creating ChromaDB client...")
        client = chromadb.PersistentClient(path="./chroma_db")
        
        try:
            # Try to get existing collection
            collection = client.get_collection(name="save_the_cat_beats")
            logging.info("Found existing collection")
            # Delete existing collection to ensure fresh data
            client.delete_collection(name="save_the_cat_beats")
            logging.info("Deleted existing collection for fresh ingestion")
            collection = client.create_collection(name="save_the_cat_beats")
        except Exception as e:
            logging.info(f"Collection not found, creating new one: {str(e)}")
            # Create new collection if it doesn't exist
            collection = client.create_collection(name="save_the_cat_beats")
            logging.info("Created new collection")
        
        return collection
    except Exception as e:
        logging.error(f"Error setting up ChromaDB: {str(e)}")
        raise

def main():
    try:
        if len(sys.argv) != 2:
            logging.error("Usage: python pdf_processor.py <pdf_file_path>")
            sys.exit(1)
            
        pdf_path = sys.argv[1]
        if not os.path.exists(pdf_path):
            logging.error(f"PDF file not found: {pdf_path}")
            sys.exit(1)
            
        logging.info(f"Processing PDF: {pdf_path}")
        
        # Extract text
        text = extract_text_from_pdf(pdf_path)
        
        # Process into beat documents
        documents = process_document(text)
        
        # Setup ChromaDB
        collection = setup_chromadb()
        
        # Add documents to ChromaDB
        logging.info("Adding documents to ChromaDB...")
        for i, doc in enumerate(documents):
            try:
                doc_id = f"{doc['type']}_{i}"
                doc_text = doc['text']
                metadata = {
                    "beat_type": doc['type'],
                    "source": os.path.basename(pdf_path),
                    "index": i
                }
                
                collection.add(
                    documents=[doc_text],
                    ids=[doc_id],
                    metadatas=[metadata]
                )
                
                if (i + 1) % 5 == 0:
                    logging.info(f"Processed {i + 1} documents...")
            except Exception as e:
                logging.error(f"Error adding document {i} to ChromaDB: {str(e)}")
        
        logging.info(f"Successfully processed and stored {len(documents)} documents in ChromaDB")
        
        # Test a query to verify ingestion
        logging.info("Testing beat retrieval...")
        test_query = "Midpoint"
        results = collection.query(
            query_texts=[f"What is the {test_query} beat?"],
            n_results=1
        )
        if results["documents"] and results["documents"][0]:
            logging.info(f"Test query successful! Found: {results['documents'][0][0][:100]}...")
        else:
            logging.warning("Test query returned no results.")
        
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 