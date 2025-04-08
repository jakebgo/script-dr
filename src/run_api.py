import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Run the FastAPI application with uvicorn"""
    uvicorn.run(
        "rag.api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True  # Enable auto-reload during development
    )

if __name__ == "__main__":
    main() 