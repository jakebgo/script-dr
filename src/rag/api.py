from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import chromadb
from chromadb.config import Settings
import logging
from typing import List, Dict, Any
from .analyzer import analyze_beat
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Script Doctor API",
    description="API for screenplay analysis using Save the Cat methodology",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ChromaDB client
try:
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_collection("save_the_cat")
    logger.info("Successfully connected to ChromaDB collection")
except Exception as e:
    logger.error(f"Error connecting to ChromaDB: {e}")
    # Don't raise exception here, handle gracefully in endpoints instead
    logger.info("Will attempt to create/reconnect to collection when needed")

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class SceneAnalysisRequest(BaseModel):
    full_outline: str = Field(..., min_length=1, description="The full screenplay outline")
    designated_beat: str = Field(..., min_length=1, description="The specific beat to analyze")
    beat_type: str = Field(..., min_length=1, description="The type of beat (e.g., Midpoint, Catalyst)")
    num_results: int = Field(default=3, ge=1, le=10, description="Number of suggestions to return")

class AnalysisResult(BaseModel):
    flag: str
    explanation: str
    suggestions: List[str]

class SceneAnalysisResponse(BaseModel):
    # Primary user-facing response focusing on synthesized analysis
    analysis: AnalysisResult

@app.get("/")
async def root():
    """Serve the main HTML page"""
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.post("/analyze", response_model=SceneAnalysisResponse)
async def analyze_scene(request: SceneAnalysisRequest):
    """
    Analyze a beat using the Save the Cat methodology
    """
    try:
        # Log the request for debugging
        logger.info(f"Analyzing beat type: {request.beat_type}")
        logger.info(f"Designated beat length: {len(request.designated_beat)} characters")
        logger.info(f"Full outline length: {len(request.full_outline)} characters")
        
        # Validate that we have all the necessary inputs
        if not request.full_outline.strip():
            raise ValueError("Full outline is required")
        
        if not request.designated_beat.strip():
            raise ValueError("Designated beat text is required")
            
        if not request.beat_type.strip():
            raise ValueError("Beat type is required")
        
        # Run the full analysis pipeline
        analysis = analyze_beat(
            outline=request.full_outline,
            beat=request.designated_beat,
            beat_type=request.beat_type
        )
        
        # Ensure analysis has all the expected keys
        if not isinstance(analysis, dict) or 'analysis' not in analysis:
            raise ValueError("Invalid analysis result format")
            
        # Extract the analysis result
        analysis_result = analysis['analysis']
        if not all(key in analysis_result for key in ['flag', 'explanation', 'suggestions']):
            raise ValueError("Missing required fields in analysis result")
            
        # Return the formatted response
        return SceneAnalysisResponse(
            analysis=AnalysisResult(
                flag=analysis_result.get('flag', 'Analysis failed'),
                explanation=analysis_result.get('explanation', 'No explanation available'),
                suggestions=analysis_result.get('suggestions', ['No suggestions available'])
            )
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        logger.error(f"Full error details: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Full error details: {error_msg}")
        if "Rate limit exceeded" in error_msg or "quota" in error_msg.lower():
            logger.error(f"API rate limit error: {e}")
            raise HTTPException(status_code=429, detail="API rate limit exceeded. Please try again later.")
        elif "Invalid response from Gemini API" in error_msg:
            logger.error(f"Invalid Gemini API response: {e}")
            raise HTTPException(status_code=500, detail="Invalid response from Gemini API")
        else:
            logger.error(f"Error analyzing beat: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    try:
        # Test ChromaDB connection 
        chroma_status = "unhealthy"
        chroma_error = None
        
        try:
            chroma_client = chromadb.PersistentClient(path="./chroma_db")
            collection = chroma_client.get_collection("save_the_cat")
            collection.count()
            chroma_status = "healthy"
        except Exception as e:
            chroma_error = str(e)
        
        return {
            "status": "healthy" if chroma_status == "healthy" else "unhealthy",
            "components": {
                "api": "healthy",
                "chromadb": chroma_status,
                "error": chroma_error
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "components": {
                "api": "healthy",
                "chromadb": "unhealthy",
                "error": str(e)
            }
        }

@app.post("/query/{collection_name}")
async def query_collection(collection_name: str, query: Dict[str, Any]):
    """Query a ChromaDB collection directly for testing purposes"""
    try:
        # Get the collection
        collection = chroma_client.get_collection(collection_name)
        
        # Execute the query
        results = collection.query(
            query_texts=query.get("query_texts", []),
            n_results=query.get("n_results", 1),
            where=query.get("where")
        )
        
        return results
    except Exception as e:
        logger.error(f"Error querying collection {collection_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 