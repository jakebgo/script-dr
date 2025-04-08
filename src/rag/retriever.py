from typing import Dict, Any, List, Tuple
import logging

# Configure logging
logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self, vector_store):
        """Initialize the retriever.
        
        Args:
            vector_store: VectorStore instance for querying documents
        """
        self.vector_store = vector_store
        
    def get_beat_definition(self, beat_type: str) -> Dict[str, Any]:
        """Retrieve the definition for a specific beat from Save the Cat.
        
        This improved implementation uses more precise querying to avoid confusion
        between similar beat types like "All Is Lost" and "Dark Night of the Soul".
        
        Args:
            beat_type (str): Name of the beat to retrieve
            
        Returns:
            Dict[str, Any]: Beat definition and metadata
        """
        logger.info(f"Retrieving definition for beat type: {beat_type}")
        
        # First try exact filtering by beat_type metadata
        try:
            # Make a more specific query that includes the exact beat type name
            query_text = f"What is the exact definition of the '{beat_type}' beat in Save the Cat? Retrieve only information about the '{beat_type}' beat and no other beats."
            
            # Try to get the exact beat definition using metadata filtering
            results = self.vector_store.query(
                collection_name="save_the_cat_beats",
                query_text=query_text,
                n_results=3,  # Get top 3 to have backup options
                where={"beat_type": beat_type}  # Exact metadata match
            )
            
            logger.info(f"Query results for {beat_type} (filtered): {len(results['documents'] or [])} documents found")
            
            # Check if we got any results with the metadata filter
            if results["documents"] and results["documents"][0]:
                # Use the top result as it should be the most relevant with the metadata filter
                logger.info(f"Found exact match for beat type: {beat_type}")
                return {
                    "definition": results["documents"][0][0],  # First document's first text
                    "metadata": results["metadatas"][0][0] if results["metadatas"] else None
                }
        except Exception as e:
            logger.warning(f"Error in metadata-filtered query: {str(e)}")
        
        # If exact metadata filtering failed, try a semantic search
        try:
            # Fall back to a very specific semantic search
            fallback_query = f"ONLY the definition of the '{beat_type}' beat in Save the Cat screenwriting framework. No other beat types."
            
            results = self.vector_store.query(
                collection_name="save_the_cat_beats",
                query_text=fallback_query,
                n_results=3  # Get top 3 to have backup options
            )
            
            logger.info(f"Query results for {beat_type} (semantic): {len(results['documents'] or [])} documents found")
            
            if not results["documents"] or not results["documents"][0]:
                logger.warning(f"No documents found for beat type: {beat_type}")
                return {
                    "definition": f"Standard definition for {beat_type} beat (fallback)",
                    "metadata": None
                }
            
            # Find the best match among the results
            best_match_idx = 0
            for i, metadata in enumerate(results["metadatas"][0]):
                if metadata.get("beat_type") == beat_type:
                    best_match_idx = i
                    break
            
            logger.info(f"Selected result {best_match_idx} as best match for {beat_type}")
            return {
                "definition": results["documents"][0][best_match_idx],
                "metadata": results["metadatas"][0][best_match_idx] if results["metadatas"] else None
            }
            
        except Exception as e:
            logger.error(f"Error retrieving beat definition: {str(e)}")
            return {
                "definition": f"Standard definition for {beat_type} beat (error fallback)",
                "metadata": None
            }
        
    def get_outline_context(
        self,
        outline_id: str,
        beat_text: str,
        n_chunks: int = 3
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant context from the outline for a given beat.
        
        Args:
            outline_id (str): ID of the outline to search
            beat_text (str): Text of the beat to find context for
            n_chunks (int): Number of relevant chunks to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of relevant outline chunks with metadata
        """
        results = self.vector_store.query(
            collection_name=f"outline_{outline_id}",
            query_text=beat_text,
            n_results=n_chunks
        )
        
        contexts = []
        for doc, metadata in zip(results["documents"], results["metadatas"]):
            contexts.append({
                "text": doc,
                "metadata": metadata
            })
            
        return contexts
        
    def get_setup_context(
        self,
        outline_id: str,
        beat_text: str,
        n_chunks: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve potential setup elements from earlier in the outline.
        
        Args:
            outline_id (str): ID of the outline to search
            beat_text (str): Text of the beat to find setups for
            n_chunks (int): Number of relevant chunks to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of potential setup elements with metadata
        """
        # Query for chunks that appear before the beat
        results = self.vector_store.query(
            collection_name=f"outline_{outline_id}",
            query_text=beat_text,
            n_results=n_chunks,
            where={"chunk_index": {"$lt": self._get_beat_chunk_index(outline_id, beat_text)}}
        )
        
        setups = []
        for doc, metadata in zip(results["documents"], results["metadatas"]):
            setups.append({
                "text": doc,
                "metadata": metadata
            })
            
        return setups
        
    def _get_beat_chunk_index(self, outline_id: str, beat_text: str) -> int:
        """Get the chunk index where the beat appears in the outline.
        
        Args:
            outline_id (str): ID of the outline
            beat_text (str): Text of the beat
            
        Returns:
            int: Chunk index where the beat appears
        """
        results = self.vector_store.query(
            collection_name=f"outline_{outline_id}",
            query_text=beat_text,
            n_results=1
        )
        
        if not results["metadatas"]:
            return -1
            
        return results["metadatas"][0]["chunk_index"] 