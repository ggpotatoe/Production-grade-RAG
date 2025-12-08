"""FastAPI main application entry point."""
import sys
from pathlib import Path

# Add parent directory to path so 'app' module can be found when running directly
# This allows running: python main.py from the backend/app/ directory
current_file = Path(__file__).resolve()
backend_dir = current_file.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import asyncio
from contextlib import asynccontextmanager

from app.models import QueryRequest, QueryResponse, HealthResponse, SearchResult
from app.services.ingestion import process_data_file, generate_embeddings
from app.services.vector_store import VectorStore
from app.services.llm_engine import LLMEngine
from app.config import settings

# Initialize services
vector_store = VectorStore()
llm_engine = None  # Will be initialized on first use

# Global flag to track ingestion status
ingestion_in_progress = False
ingestion_completed = False

async def background_ingestion():
    """Background task for data ingestion."""
    global ingestion_in_progress, ingestion_completed
    
    if ingestion_in_progress or ingestion_completed:
        return
    
    ingestion_in_progress = True
    
    try:
        # Check Qdrant connection first
        if not vector_store.is_connected():
            print("WARNING: Qdrant is not accessible. Please start it with: docker-compose up -d")
            print("The server will start, but queries will fail until Qdrant is available.")
            ingestion_in_progress = False
            return
        
        # Check if collection exists, if not, create and populate it
        if not vector_store.collection_exists():
            print("Collection does not exist. Starting background ingestion...")
            
            # Process data file - try multiple possible paths
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            data_path = os.path.join(project_root, "data", "ad users.xlsx")
            
            if not os.path.exists(data_path):
                # Try alternative path
                data_path = os.path.join(current_dir, "..", "..", "data", "ad users.xlsx")
                data_path = os.path.abspath(data_path)
            
            if not os.path.exists(data_path):
                data_path = settings.DATA_PATH
                if not os.path.exists(data_path):
                    print(f"ERROR: Data file not found at {data_path}")
                    print("Please ensure the data file exists. The server will start, but queries will fail.")
                    ingestion_in_progress = False
                    return
            
            print(f"Processing data file: {data_path}")
            documents, metadatas = process_data_file(data_path)
            
            # Generate embeddings (this is CPU-intensive, run in background)
            print("Generating embeddings... (this may take several minutes)")
            # Run CPU-intensive task in thread pool
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(None, generate_embeddings, documents)
            
            # Create collection with correct vector size
            vector_size = len(embeddings[0]) if embeddings else 1024
            vector_store.create_collection(vector_size=vector_size)
            
            # Insert documents
            print("Inserting documents into vector store...")
            vector_store.upsert_documents(embeddings, documents, metadatas)
            print("✅ Data ingestion completed!")
            ingestion_completed = True
        else:
            print("Collection already exists. Skipping ingestion.")
            ingestion_completed = True
    except Exception as e:
        print(f"ERROR during background data ingestion: {e}")
        import traceback
        traceback.print_exc()
        print("The server will continue running, but queries may fail.")
    finally:
        ingestion_in_progress = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Start background ingestion task
    print("🚀 Starting server...")
    print("Server is ready! Data ingestion is running in the background.")
    asyncio.create_task(background_ingestion())
    yield
    # Shutdown: cleanup if needed
    print("Shutting down...")

app = FastAPI(
    title="Óbuda University Phonebook RAG API",
    description="RAG API for searching the university phonebook",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS, assets) - must be before routes
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
frontend_path = project_root / "frontend"

if frontend_path.exists():
    # Mount static files directory for CSS, JS, and assets
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Initialize services
vector_store = VectorStore()
llm_engine = None  # Will be initialized on first use

def initialize_llm():
    """Lazy initialization of LLM engine."""
    global llm_engine
    if llm_engine is None:
        try:
            llm_engine = LLMEngine()
        except ValueError as e:
            print(f"Warning: LLM engine not initialized: {e}")
    return llm_engine

@app.get("/")
async def root():
    """Root endpoint - serves index.html from mounted static files."""
    # Use the same path as the static mount
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    else:
        return {"message": "Óbuda University Phonebook RAG API", "error": "Frontend not found"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    is_connected = vector_store.is_connected()
    collection_exists = vector_store.collection_exists() if is_connected else False
    
    # Check collection info if it exists
    collection_info = None
    if is_connected and collection_exists:
        try:
            collection_info = vector_store.client.get_collection(vector_store.collection_name)
        except:
            pass
    
    return HealthResponse(
        status="healthy" if is_connected and collection_exists else "degraded",
        qdrant_connected=is_connected,
        collection_exists=collection_exists
    )

@app.get("/collection-info")
async def collection_info():
    """Get information about the collection."""
    if not vector_store.is_connected():
        return {"error": "Qdrant not connected"}
    
    if not vector_store.collection_exists():
        return {"error": "Collection does not exist"}
    
    try:
        # Use count_points instead of get_collection to avoid Pydantic validation issues
        collection_name = vector_store.collection_name
        
        # Count points in the collection
        try:
            count_result = vector_store.client.count(collection_name=collection_name)
            points_count = count_result.count if hasattr(count_result, 'count') else 0
        except Exception as e:
            points_count = None
        
        # Try to get collection info with error handling
        result = {
            "name": collection_name,
            "points_count": points_count,
        }
        
        # Try to get collection info, but catch Pydantic validation errors
        try:
            info = vector_store.client.get_collection(collection_name)
            if hasattr(info, 'points_count'):
                result["points_count"] = info.points_count
            if hasattr(info, 'vectors_count'):
                result["vectors_count"] = info.vectors_count
        except Exception as e:
            # If get_collection fails due to Pydantic validation, we still have the count
            result["warning"] = "Could not retrieve full collection info due to version mismatch"
            result["error_details"] = str(e)
        
        return result
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Process a natural language query and return an answer.
    
    Args:
        request: Query request with query text and language
        
    Returns:
        Query response with answer and sources
    """
    try:
        # Initialize LLM if needed
        llm = initialize_llm()
        if llm is None:
            raise HTTPException(
                status_code=500,
                detail="LLM engine not available. Please check OPENAI_API_KEY."
            )
        
        # Check if collection exists and has data
        if not vector_store.collection_exists():
            if request.language == "hu":
                answer = "Az adatbázis még nincs betöltve. Kérlek várj egy pillanatot, majd próbáld újra."
            else:
                answer = "Database is not loaded yet. Please wait a moment and try again."
            return QueryResponse(
                answer=answer,
                sources=[],
                language=request.language
            )
        
        # Generate query embedding with "query:" prefix for E5 model
        query_text = f"query: {request.query}"
        print(f"Generating embedding for query: {request.query}")
        query_embeddings = generate_embeddings([query_text])
        query_embedding = query_embeddings[0]
        print(f"Query embedding generated, vector size: {len(query_embedding)}")
        
        # Search in vector store
        print(f"Searching in collection '{vector_store.collection_name}' with top_k={request.top_k}")
        search_results = vector_store.search(
            query_embedding=query_embedding,
            top_k=request.top_k
        )
        print(f"Search returned {len(search_results)} results")
        
        if not search_results:
            # No results found
            if request.language == "hu":
                answer = "Sajnos nem találtam találatot a telefonkönyvben a keresésre."
            else:
                answer = "Sorry, I couldn't find any results in the phonebook for your search."
            
            return QueryResponse(
                answer=answer,
                sources=[],
                language=request.language
            )
        
        # Generate answer using LLM
        answer = llm.generate_answer(
            query=request.query,
            context=search_results,
            language=request.language
        )
        
        # Format search results for response
        formatted_results = [
            SearchResult(
                score=result["score"],
                metadata=result["metadata"],
                content=result["content"]
            )
            for result in search_results
        ]
        
        return QueryResponse(
            answer=answer,
            sources=formatted_results,
            language=request.language
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

async def _reindex_internal():
    """Internal reindexing function."""
    # Delete existing collection
    if vector_store.collection_exists():
        vector_store.delete_collection()
    
    # Process and ingest data - try multiple possible paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    data_path = os.path.join(project_root, "data", "ad users.xlsx")
    
    if not os.path.exists(data_path):
        # Try alternative path
        data_path = os.path.join(current_dir, "..", "..", "data", "ad users.xlsx")
        data_path = os.path.abspath(data_path)
    
    if not os.path.exists(data_path):
        data_path = settings.DATA_PATH
    
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail=f"Data file not found at {data_path}")
    
    print(f"Starting reindexing with file: {data_path}")
    documents, metadatas = process_data_file(data_path)
    
    print("Generating embeddings...")
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    embeddings = await loop.run_in_executor(None, generate_embeddings, documents)
    
    vector_size = len(embeddings[0]) if embeddings else 1024
    vector_store.create_collection(vector_size=vector_size)
    
    print("Inserting documents...")
    vector_store.upsert_documents(embeddings, documents, metadatas)
    
    return {"message": "Reindexing completed successfully", "documents_count": len(documents)}

@app.post("/reindex")
@app.get("/reindex")
async def reindex():
    """Reindex the data (useful for updating the vector store). Supports both GET and POST."""
    try:
        result = await _reindex_internal()
        return result
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during reindexing: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

