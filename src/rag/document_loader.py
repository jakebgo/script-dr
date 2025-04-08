from pathlib import Path
from typing import List, Dict, Any
import json
import uuid
import os
import logging
import re
from PyPDF2 import PdfReader
from .vector_store import VectorStore

# Configure logging
logger = logging.getLogger(__name__)

class DocumentLoader:
    def __init__(self, vector_store=None):
        """Initialize the document loader.
        
        Args:
            vector_store: VectorStore instance for storing documents
        """
        self.vector_store = vector_store or VectorStore()
        
    def load_framework_document(self, file_path: str) -> None:
        """Load and index the framework document (e.g., Save the Cat PDF/TXT).
        
        This is a one-time ingestion process that:
        1. Loads the document
        2. Extracts beat definitions
        3. Generates embeddings
        4. Stores in ChromaDB
        
        Args:
            file_path (str): Path to the framework document
        """
        logger.info(f"Loading framework document: {file_path}")
        
        # Determine file extension
        _, ext = os.path.splitext(file_path)
        
        # Load document based on file type
        if ext.lower() == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
                beat_documents = self._process_json_beats(data)
        elif ext.lower() == '.txt':
            with open(file_path, 'r') as f:
                text = f.read()
                beat_documents = self._extract_beats_from_text(text)
        elif ext.lower() == '.pdf':
            # Extract text from PDF using PyPDF2
            text = self._extract_text_from_pdf(file_path)
            beat_documents = self._extract_beats_from_text(text)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
            
        # Create collection for framework document beats
        collection_name = "save_the_cat"
        
        # Check if collection exists and delete if it does
        try:
            existing_collections = self.vector_store.list_collections()
            if collection_name in existing_collections:
                logger.info(f"Deleting existing collection: {collection_name}")
                self.vector_store.delete_collection(collection_name)
        except Exception as e:
            logger.warning(f"Error checking existing collections: {str(e)}")
        
        # Create the collection
        self.vector_store.create_collection(
            name=collection_name,
            metadata={"source": "Save the Cat", "type": "beat_definitions"}
        )
        
        # Add beat documents to the collection
        documents = []
        ids = []
        metadatas = []
        
        logger.info(f"Adding {len(beat_documents)} beat documents to collection")
        
        for i, beat_doc in enumerate(beat_documents):
            documents.append(beat_doc["text"])
            ids.append(f"{beat_doc['type']}_{i}")
            metadatas.append({
                "beat_type": beat_doc["type"],
                "source": os.path.basename(file_path),
                "index": i
            })
            
        # Add all beat documents to the collection
        self.vector_store.add_documents(
            collection_name=collection_name,
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        logger.info(f"Successfully loaded framework document with {len(beat_documents)} beat definitions")
        
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from a PDF file.
        
        Args:
            file_path (str): Path to PDF file
            
        Returns:
            str: Extracted text
        """
        try:
            reader = PdfReader(file_path)
            logger.info(f"Total pages in PDF: {len(reader.pages)}")
            
            text = ""
            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    logger.info(f"Processing page {i+1}/{len(reader.pages)} - Extracted {len(page_text)} characters")
                    text += page_text + "\n"
                except Exception as e:
                    logger.error(f"Error processing page {i+1}: {str(e)}")
            
            logger.info(f"Total text extracted: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error opening PDF {file_path}: {str(e)}")
            raise

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text.
        
        Args:
            text (str): Text to clean
            
        Returns:
            str: Cleaned text
        """
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove multiple newlines
        text = re.sub(r'\n\s*\n', '\n', text)
        return text.strip()
        
    def _extract_beats_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract individual beat definitions from framework document text.
        
        Args:
            text (str): Text to process
            
        Returns:
            List[Dict[str, str]]: List of beat documents
        """
        logger.info("Extracting beat definitions from text...")
        
        # Clean the text
        text = self._clean_text(text)
        
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
            
            logger.info(f"Extracted beat: {beat_type} ({len(description)} chars)")
        
        logger.info(f"Total beats extracted: {len(beat_documents)}")
        
        # If we didn't find any beat definitions, fall back to chunking
        if not beat_documents:
            logger.warning("No beat definitions extracted! Falling back to text chunking method.")
            chunks = self._chunk_text_with_overlap(text)
            for i, chunk in enumerate(chunks):
                beat_documents.append({
                    "type": f"chunk_{i}",
                    "text": chunk
                })
        
        return beat_documents
        
    def _process_json_beats(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Process beat definitions from JSON format.
        
        Args:
            data (Dict[str, Any]): JSON data with beat definitions
            
        Returns:
            List[Dict[str, str]]: List of beat documents
        """
        beat_documents = []
        
        if "beats" in data:
            for beat in data["beats"]:
                beat_type = beat.get("name", "Unknown Beat")
                description = beat.get("description", "")
                
                # Create a structured document for this beat
                beat_doc = f"BEAT TYPE: {beat_type}\n\nDEFINITION: {description}\n\nThis is the '{beat_type}' beat according to the Save the Cat screenplay structure framework."
                
                beat_documents.append({
                    "type": beat_type,
                    "text": beat_doc
                })
                
                logger.info(f"Processed beat from JSON: {beat_type}")
                
        logger.info(f"Total beats from JSON: {len(beat_documents)}")
        return beat_documents
        
    def _chunk_text_with_overlap(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Split text into chunks with overlap.
        
        Args:
            text (str): Text to split
            chunk_size (int): Target size for each chunk
            overlap (int): Number of characters to overlap between chunks
            
        Returns:
            List[str]: List of text chunks
        """
        logger.info(f"Starting text chunking with chunk_size={chunk_size}, overlap={overlap}")
        
        # First split into sentences using common sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        logger.info(f"Split text into {len(sentences)} sentences")
        
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
        
        logger.info(f"Created {len(chunks)} chunks with average length {sum(len(c) for c in chunks)/len(chunks) if chunks else 0:.2f}")
        
        return chunks

    def load_outline(self, outline_text: str, outline_id: str) -> None:
        """Load and index a screenplay outline.
        
        Args:
            outline_text (str): The full outline text
            outline_id (str): Unique identifier for this outline
        """
        logger.info(f"Loading outline with ID: {outline_id}")
        
        collection_name = f"outline_{outline_id}"
        self.vector_store.create_collection(
            name=collection_name,
            metadata={"type": "screenplay_outline", "id": outline_id}
        )
        
        # Split outline into chunks
        chunks = self._chunk_text_with_overlap(outline_text)
        
        documents = []
        ids = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            ids.append(f"{outline_id}_chunk_{i}")
            metadatas.append({
                "chunk_index": i,
                "outline_id": outline_id
            })
            
        self.vector_store.add_documents(
            collection_name=collection_name,
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        logger.info(f"Successfully indexed outline with ID: {outline_id} ({len(chunks)} chunks)") 