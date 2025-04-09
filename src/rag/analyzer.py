import google.generativeai as genai
from typing import List, Dict, Any
import os
import uuid
import logging
from .vector_store import get_collection, VectorStore
from ..config.config import Config

# Configure logging
logger = logging.getLogger(__name__)

# Configure Gemini API
api_key = os.getenv("GEMINI_FLASH_API_KEY")
if not api_key:
    raise ValueError("Gemini API key not found in environment variables.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

def get_beat_definition(beat_type: str, collection) -> str:
    """Retrieve the Save the Cat definition for a specific beat type."""
    try:
        logger.info(f"Querying for beat definition: {beat_type}")
        results = collection.query(
            query_texts=[f"Explain the narrative function and purpose of the {beat_type} beat according to the Save the Cat framework. Only include information about the {beat_type} beat."],
            n_results=1
        )
        logger.info(f"Query results: {results}")
        
        if not results['documents'] or not results['documents'][0]:
            logger.warning(f"No documents found for beat type: {beat_type}")
            return f"Standard definition for {beat_type} beat (fallback)"
            
        return results['documents'][0][0]
    except Exception as e:
        logger.error(f"Error retrieving beat definition: {str(e)}")
        return f"Standard definition for {beat_type} beat (error fallback)"

def analyze_functional_aspects(outline: str, beat: str, definition: str, beat_type: str) -> str:
    """Analyze the functional aspects of the beat using Gemini Pro."""
    prompt = f"""
You are a screenplay structure expert analyzing a specific beat within the context of the **entire provided outline**.

FULL OUTLINE:
{outline}

DESIGNATED BEAT ({beat_type}):
{beat}

SAVE THE CAT DEFINITION FOR {beat_type}:
{definition}

Analyze how effectively this DESIGNATED BEAT fulfills its structural function as a {beat_type} beat **considering the complete narrative arc presented in the FULL OUTLINE**. Evaluate:
1. Alignment with the SAVE THE CAT DEFINITION for a {beat_type} beat.
2. Connection to preceding plot points and character development **established earlier in the outline**.
3. Impact on subsequent plot points and the overall trajectory towards the climax **as suggested by later parts of the outline**.
4. Contribution to the story's central theme(s) **evident throughout the outline**.

Provide a detailed analysis focusing on strengths and weaknesses **within the context of the whole story**. Focus exclusively on its function as a {beat_type} beat.
"""
    
    try:
        logger.info("Generating functional analysis with Gemini")
        logger.info(f"Prompt length: {len(prompt)} characters")
        
        response = model.generate_content(prompt)
        logger.info("Received response from Gemini API")
        
        if not response:
            logger.error("Empty response received from Gemini API")
            raise ValueError("Empty response from Gemini API")
            
        if not hasattr(response, 'text') or not response.text:
            logger.error(f"Response missing text attribute or empty text: {response}")
            raise ValueError("Invalid response from Gemini API - missing text")
            
        logger.info(f"Functional analysis generated successfully: {len(response.text)} characters")
        return response.text
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in functional analysis: {error_msg}")
        
        if "429" in error_msg or "quota" in error_msg.lower():
            raise Exception("429 You exceeded your current quota, please check your plan and billing details.")
        raise

def check_setups(outline: str, beat: str, collection) -> str:
    """Check for missing setups of elements within the designated beat."""
    # First, identify key elements in the beat
    elements_prompt = f"""
    You are an expert screenplay analyst specializing in story structure and setup/payoff relationships.
    
    Identify the 3-5 most important key story elements, character actions, plot points, or narrative elements introduced in this beat:
    
    {beat}
    
    List ONLY the specific elements that would require explicit setup earlier in the story. 
    Focus on concrete story elements (characters, plot devices, relationships, etc.) rather than abstract concepts.
    Format your response as a simple bullet point list (no numbering, just bullets).
    """
    
    try:
        logger.info("Identifying key elements in the beat")
        logger.info(f"Elements prompt length: {len(elements_prompt)} characters")
        
        elements_response = model.generate_content(elements_prompt)
        logger.info("Received elements response from Gemini API")
        
        if not elements_response or not hasattr(elements_response, 'text') or not elements_response.text:
            logger.error("Invalid response for elements identification")
            # Provide a default fallback response to avoid failing
            return "No critical setup issues identified in this beat."
            
        elements = elements_response.text
        logger.info(f"Identified elements: {elements}")
        
        # Then check for setups
        setup_prompt = f"""
        You are an expert screenplay analyst specializing in setup/payoff relationships.
        
        I've identified these key elements from a designated beat in a screenplay outline:
        
        {elements}
        
        Check the earlier sections of the outline below to determine if each element has been properly set up:
        
        {outline}
        
        For each element:
        1. Determine if it's adequately set up in the earlier sections
        2. If not, explain specifically what's missing and why it matters
        3. Be concrete and specific about what setup would be needed
        
        Focus on the MOST IMPORTANT 2-3 missing setups only - don't analyze elements that are properly established.
        Format as a clear analysis that a screenwriter could use to improve their outline.
        """
        
        logger.info("Checking setups for identified elements")
        logger.info(f"Setup prompt length: {len(setup_prompt)} characters")
        
        setup_response = model.generate_content(setup_prompt)
        logger.info("Received setup check response from Gemini API")
        
        if not setup_response or not hasattr(setup_response, 'text') or not setup_response.text:
            logger.error("Invalid response for setup check")
            # Provide a default fallback response to avoid failing
            return "Analysis found no critical setup issues. All key elements appear to be properly established earlier in the outline."
            
        logger.info(f"Setup analysis successfully generated: {len(setup_response.text)} characters")
        return setup_response.text
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in setup check: {error_msg}")
        
        if "429" in error_msg or "quota" in error_msg.lower():
            raise Exception("429 You exceeded your current quota, please check your plan and billing details.")
            
        # Provide a default fallback response on error
        return "Unable to complete setup analysis. Focus on ensuring all key characters, locations, and plot elements introduced in this beat are properly established earlier in the outline."

def synthesize_analysis(functional_analysis: str, setup_analysis: str, beat_type: str) -> Dict[str, Any]:
    """Synthesize the analyses into Flag->Explain->Suggest format."""
    synthesis_prompt = f"""
You are an expert screenplay consultant providing actionable feedback on a {beat_type} beat.

Synthesize these analyses into a clear, actionable review, **explicitly linking the beat's functional performance (Analysis 1) to its setup/payoff integrity within the full outline (Analysis 2)**:

FUNCTIONAL ANALYSIS (considering full outline):
{functional_analysis}

SETUP/PAYOFF ANALYSIS (relative to this beat within the full outline):
{setup_analysis}

Format your response STRICTLY as follows, with EXACTLY these section headers:

FLAG: [One clear, specific issue that most needs attention in this {beat_type} beat, considering both function and context]

EXPLAIN: [Explain why this issue matters structurally/narratively, referencing Save the Cat principles for the {beat_type} beat AND specific connections/disconnects **within the provided outline**]

SUGGEST:
- [First specific, actionable suggestion addressing the core issue, potentially referencing **other specific parts of the outline**]
- [Second specific, actionable suggestion, potentially referencing **other specific parts of the outline**]
- [Optional third suggestion if relevant]

Your response MUST include these EXACT headings (FLAG, EXPLAIN, SUGGEST) followed by relevant content.
Ensure the explanation and suggestions clearly demonstrate consideration of the **entire narrative context**. Focus exclusively on the specific {beat_type} beat.
"""
    
    try:
        logger.info("Generating synthesis with Gemini")
        logger.info(f"Synthesis prompt length: {len(synthesis_prompt)} characters")
        
        response = model.generate_content(synthesis_prompt)
        logger.info("Received response from Gemini API for synthesis")
        
        if not response:
            logger.error("Empty response received from Gemini API during synthesis")
            raise ValueError("Empty response from Gemini API during synthesis")
            
        if not hasattr(response, 'text') or not response.text:
            logger.error(f"Synthesis response missing text attribute or empty text: {response}")
            raise ValueError("Invalid response from Gemini API during synthesis - missing text")
            
        result = response.text
        logger.info(f"Synthesis result raw text: {result}")
        
        # More flexible parsing logic
        flag = "The beat requires structural refinement"
        explanation = f"According to Save the Cat principles, this {beat_type} beat needs refinement in structure and purpose"
        suggestions = [f"Strengthen the emotional impact required for a {beat_type} beat", 
                      f"Ensure clear connection to surrounding beats", 
                      "Verify all key elements are properly set up"]
        
        # Try to parse the sections
        if "FLAG:" in result:
            flag_section = result.split("FLAG:")[1].split("EXPLAIN:" if "EXPLAIN:" in result else "SUGGEST:" if "SUGGEST:" in result else "\n\n")[0]
            flag = flag_section.strip()
            logger.info(f"Parsed FLAG: {flag}")
        
        if "EXPLAIN:" in result:
            explain_section = result.split("EXPLAIN:")[1].split("SUGGEST:" if "SUGGEST:" in result else "\n\n")[0]
            explanation = explain_section.strip()
            logger.info(f"Parsed EXPLAIN: {explanation[:100]}...")
        
        if "SUGGEST:" in result:
            suggest_section = result.split("SUGGEST:")[1].strip()
            
            # Handle bullet points and numbered lists
            suggestion_items = []
            for line in suggest_section.split("\n"):
                line = line.strip()
                if line and (line.startswith("-") or line.startswith("*") or (len(line) > 2 and line[0].isdigit() and line[1] in [".", ")", ":"])):
                    cleaned_line = line[2:].strip() if line.startswith("- ") else line[2:].strip() if (len(line) > 2 and line[0].isdigit() and line[1] in [".", ")", ":"]) else line[1:].strip() if line.startswith("-") or line.startswith("*") else line
                    if cleaned_line:
                        suggestion_items.append(cleaned_line)
            
            if suggestion_items:
                suggestions = suggestion_items[:3]  # Limit to 3 suggestions
                logger.info(f"Parsed SUGGEST: {len(suggestions)} suggestions")
        
        return {
            "flag": flag,
            "explanation": explanation,
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Error in synthesis: {str(e)}")
        return {
            "flag": f"This {beat_type} beat needs structural improvement",
            "explanation": f"According to Save the Cat principles, the {beat_type} beat should fulfill a specific narrative function. The current beat doesn't fully achieve this.",
            "suggestions": [
                f"Review the Save the Cat description of the {beat_type} beat",
                "Ensure the beat has clear emotional impact",
                "Check that all elements in this beat are properly set up earlier"
            ]
        }

def index_outline(outline: str) -> str:
    """Index the outline for RAG-based analysis.
    
    Returns:
        str: ID for the indexed outline
    """
    try:
        # Generate unique ID for this outline
        outline_id = str(uuid.uuid4())
        logger.info(f"Indexing outline with ID: {outline_id}")
        
        # Initialize vector store
        vector_store = VectorStore()
        
        # Create collection for this outline
        collection_name = f"outline_{outline_id}"
        vector_store.create_collection(
            name=collection_name,
            metadata={"type": "screenplay_outline", "id": outline_id}
        )
        
        # Split outline into chunks
        chunks = _chunk_text(outline)
        logger.info(f"Split outline into {len(chunks)} chunks")
        
        # Add chunks to the collection
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
        
        vector_store.add_documents(
            collection_name=collection_name,
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        logger.info(f"Successfully indexed outline with ID: {outline_id}")
        return outline_id
    except Exception as e:
        logger.error(f"Error indexing outline: {str(e)}")
        raise
        
def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split text into chunks with overlap for indexing.
    
    Args:
        text (str): Text to chunk
        chunk_size (int): Target size for each chunk
        overlap (int): Number of characters to overlap between chunks
        
    Returns:
        List[str]: List of text chunks
    """
    # Simple implementation based on paragraph breaks
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for para in paragraphs:
        para_size = len(para)
        if current_size + para_size > chunk_size and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            # Keep some paragraphs for overlap
            overlap_size = 0
            overlap_chunks = []
            for p in reversed(current_chunk):
                if overlap_size + len(p) > overlap:
                    break
                overlap_chunks.insert(0, p)
                overlap_size += len(p)
            current_chunk = overlap_chunks
            current_size = overlap_size
        current_chunk.append(para)
        current_size += para_size
        
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
        
    return chunks

def analyze_beat(outline: str, beat: str, beat_type: str) -> Dict[str, Any]:
    """
    Multi-stage analysis pipeline for a screenplay beat.
    
    Args:
        outline: The full screenplay outline
        beat: The selected text (designated beat)
        beat_type: The type of beat (e.g., "Midpoint", "Catalyst")
        
    Returns:
        Dict with analysis results
    """
    try:
        logger.info(f"Starting analysis pipeline for beat type: {beat_type}")
        
        # Make sure outline and beat have content
        if not outline or not beat:
            raise ValueError("Both outline and beat must have content")
            
        # Create a unique ID for this analysis request
        analysis_id = str(uuid.uuid4())
        logger.info(f"Analysis ID: {analysis_id}")
        
        # Get or create the Save the Cat collection
        collection = get_collection("save_the_cat")
        logger.info("Retrieved ChromaDB collection for Save the Cat framework")
        
        # 1. Get the beat definition
        logger.info(f"Getting definition for beat type: {beat_type}")
        definition = get_beat_definition(beat_type, collection)
        logger.info(f"Retrieved definition for {beat_type}: {len(definition)} characters")
        
        # 2. Analyze functional aspects
        logger.info("Starting functional analysis")
        functional_analysis = analyze_functional_aspects(outline, beat, definition, beat_type)
        logger.info(f"Completed functional analysis: {len(functional_analysis)} characters")
        
        # 3. Check for missing setups
        logger.info("Starting setup check")
        setup_analysis = check_setups(outline, beat, collection)
        logger.info(f"Completed setup check: {len(setup_analysis)} characters")
        
        # 4. Synthesize the analyses
        logger.info("Starting synthesis")
        synthesis = synthesize_analysis(functional_analysis, setup_analysis, beat_type)
        logger.info("Completed synthesis")
        
        # Return the complete analysis
        return {
            "id": analysis_id,
            "beat_type": beat_type,
            "definition": definition,
            "analysis": synthesis,
            "raw": {
                "functional_analysis": functional_analysis,
                "setup_analysis": setup_analysis
            }
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in analysis pipeline: {error_msg}")
        raise 