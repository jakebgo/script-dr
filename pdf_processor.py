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

def chunk_text(text, chunk_size=1000, overlap=100):
    """
    Split text into overlapping chunks while preserving sentence integrity.
    """
    logging.info(f"Starting text chunking with chunk_size={chunk_size}, overlap={overlap}")
    logging.info(f"Total text length: {len(text)} characters")
    
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
    
    # Log chunk statistics
    chunk_lengths = [len(chunk) for chunk in chunks]
    logging.info(f"Finished chunking. Created {len(chunks)} chunks")
    logging.info("Chunk statistics:")
    logging.info(f"  Average length: {sum(chunk_lengths)/len(chunk_lengths):.2f} characters")
    logging.info(f"  Min length: {min(chunk_lengths)} characters")
    logging.info(f"  Max length: {max(chunk_lengths)} characters")
    if chunks:
        sample = chunks[0][:200] + "..."
        logging.info(f"  Sample of first chunk: {sample}")
    
    return chunks

def process_document(text):
    """Process the document text into chunks for ChromaDB ingestion."""
    # Clean the text
    logging.info("Cleaning text...")
    text = clean_text(text)
    logging.info(f"Text length after cleaning: {len(text)} characters")
    
    # Split into chunks with overlap
    logging.info("Splitting text into chunks...")
    chunks = chunk_text(text)
    
    logging.info(f"Total chunks created: {len(chunks)}")
    avg_length = sum(len(c) for c in chunks) / len(chunks) if chunks else 0
    logging.info(f"Average chunk length: {avg_length:.2f} characters")
    
    # Log a sample of the first chunk
    if chunks:
        logging.info(f"Sample of first chunk: {chunks[0][:200]}...")
    
    return chunks

def setup_chromadb():
    """Initialize ChromaDB."""
    logging.info("Setting up ChromaDB...")
    try:
        # Create client and collection
        logging.info("Creating ChromaDB client...")
        client = chromadb.PersistentClient(path="./chroma_db")
        
        try:
            # Try to get existing collection
            collection = client.get_collection(name="save_the_cat")
            logging.info("Found existing collection")
        except Exception as e:
            logging.info(f"Collection not found, creating new one: {str(e)}")
            # Create new collection if it doesn't exist
            collection = client.create_collection(name="save_the_cat")
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
        
        # Process into chunks
        chunks = process_document(text)
        
        # Setup ChromaDB
        collection = setup_chromadb()
        
        # Add chunks to ChromaDB
        logging.info("Adding chunks to ChromaDB...")
        for i, chunk in enumerate(chunks):
            try:
                collection.add(
                    documents=[chunk],
                    ids=[f"chunk_{i}"],
                    metadatas=[{"source": os.path.basename(pdf_path), "chunk_index": i}]
                )
                if (i + 1) % 10 == 0:
                    logging.info(f"Processed {i + 1} chunks...")
            except Exception as e:
                logging.error(f"Error adding chunk {i} to ChromaDB: {str(e)}")
        
        logging.info(f"Successfully processed and stored {len(chunks)} chunks in ChromaDB")
        
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 