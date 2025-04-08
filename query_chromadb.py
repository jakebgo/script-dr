import chromadb
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_chromadb():
    """Initialize ChromaDB."""
    # Create client and get collection
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection(name="save_the_cat")
    return collection

def main():
    try:
        # Get the collection
        collection = setup_chromadb()
        
        # Get collection info
        logging.info("Collection information:")
        logging.info(f"Collection count: {collection.count()}")
        
        # Try a sample query
        query = "What is the opening image beat?"
        results = collection.query(
            query_texts=[query],
            n_results=2
        )
        
        logging.info("\nQuery results for: %s", query)
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            logging.info(f"\nResult {i + 1}:")
            logging.info(f"Beat Type: {metadata.get('beat_type', 'Unknown')}")
            logging.info(f"Source: {metadata.get('source', 'Unknown')}")
            logging.info(f"Index: {metadata.get('index', 'Unknown')}")
            logging.info(f"Content: {doc[:500]}...")
        
        # Query for specific beat types
        beat_types = ["Opening Image", "Catalyst", "Midpoint", "All Is Lost", "Dark Night of the Soul", "Break into Three", "Finale"]
        
        logging.info("\n\nBeat Type Verification:")
        for beat_type in beat_types:
            results = collection.query(
                query_texts=[f"What is the {beat_type} beat?"],
                n_results=1,
                where={"beat_type": beat_type}
            )
            
            if results['documents'][0]:
                logging.info(f"\n✅ Found definition for: {beat_type}")
                logging.info(f"Metadata: {results['metadatas'][0][0]}")
                logging.info(f"Content excerpt: {results['documents'][0][0][:150]}...")
            else:
                logging.info(f"\n❌ No definition found for: {beat_type}")
            
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 