from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from datetime import datetime
import logging
from pathlib import Path
import os

from app.config import settings
from app.models.schemas import HealthResponse
from app.api import upload, processing
from app.services.audio_processor import audio_processor
from app.services.ai_analyzer import ai_analyzer

# Ensure ffmpeg and graphviz are in PATH (Windows fix)
extra_paths = [
    r"C:\ffmpeg",
    r"C:\Program Files\Graphviz\bin",
    r"C:\Program Files (x86)\Graphviz\bin",
]

for path in extra_paths:
    if os.path.exists(path) and path not in os.environ.get('PATH', ''):
        os.environ['PATH'] = path + os.pathsep + os.environ.get('PATH', '')
        print(f"Added to PATH: {path}")

logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file) if settings.log_file else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered assistant for workflow generation and document completion",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(processing.router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    
    # Verify models are loaded
    logger.info("Checking AI models...")
    if not audio_processor.is_ready():
        logger.warning("Audio processor not ready")
    if not ai_analyzer.is_ready():
        logger.warning("AI analyzer not ready")
    
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        models_loaded={
            "whisper": audio_processor.is_ready(),
            "llama": ai_analyzer.is_ready()
        },
        timestamp=datetime.now()
    )


@app.get("/download/workflow/{workflow_id}/{file_type}")
async def download_workflow(workflow_id: str, file_type: str):
    """
    Download workflow file
    
    Args:
        workflow_id: Workflow ID
        file_type: 'xml' or 'diagram'
    """
    if file_type == "xml":
        # Legacy support or if requested as xml
        file_path = settings.workflow_output_dir / f"workflow_{workflow_id}.xml"
        if not file_path.exists():
             file_path = settings.workflow_output_dir / f"workflow_{workflow_id}.bpmn"
        media_type = "application/xml"
    elif file_type == "bpmn":
        file_path = settings.workflow_output_dir / f"workflow_{workflow_id}.bpmn"
        media_type = "application/xml"
    elif file_type == "diagram":
        file_path = settings.workflow_output_dir / f"workflow_{workflow_id}.{settings.diagram_format}"
        media_type = f"image/{settings.diagram_format}"
    else:
        return {"error": "Invalid file type. Use 'bpmn', 'xml' or 'diagram'"}
    
    if not file_path.exists():
        return {"error": "File not found"}
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=file_path.name
    )


@app.get("/download/document/{document_id}")
async def download_document(document_id: str):
    """Download completed document"""
    # Search for document
    for file_path in settings.output_dir.glob(f"completed_{document_id}.*"):
        return FileResponse(
            path=file_path,
            filename=file_path.name
        )
    
    return {"error": "Document not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        reload_dirs=["app"]
    )
