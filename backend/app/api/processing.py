from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import uuid
from pathlib import Path
import logging
import json

from app.config import settings
from app.models.schemas import (
    ProcessRequest,
    ProcessResponse,
    ProcessingStatus,
    TranscriptionResult,
    WorkflowDiagram,
    CompletedDocument
)
from app.services.audio_processor import audio_processor
from app.services.document_processor import document_processor
from app.services.ai_analyzer import ai_analyzer
from app.services.workflow_generator import workflow_generator
from app.services.template_filler import template_filler
from app.services.orchestrator import workflow_orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["processing"])

jobs = {}


@router.post("/transcribe/{file_id}", response_model=TranscriptionResult)
async def transcribe_audio(file_id: str, language: Optional[str] = None):
    try:
        # Find audio file
        audio_path = None
        for ext in settings.allowed_audio_formats:
            potential_path = settings.upload_dir / f"{file_id}{ext}"
            if potential_path.exists():
                audio_path = potential_path
                break
        
        if not audio_path:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Transcribe
        result = await audio_processor.transcribe_audio(
            audio_path, file_id, language
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/audio")
async def process_audio_to_workflow(
    file_id: str,
    workflow_name: Optional[str] = None,
    language: Optional[str] = None
):
    """
    Strict pipeline: Audio ID -> Transcription -> Steps -> XML
    """
    try:
        # Find audio file
        audio_path = None
        for ext in settings.allowed_audio_formats:
            potential_path = settings.upload_dir / f"{file_id}{ext}"
            if potential_path.exists():
                audio_path = potential_path
                break
        
        if not audio_path:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Run orchestrated workflow
        workflow = await workflow_orchestrator.audio_to_diagram(
            audio_path, file_id, workflow_name, language
        )
        
        return workflow
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio-to-workflow processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/{workflow_id}", response_model=WorkflowDiagram)
async def get_workflow(workflow_id: str):
    """Get workflow diagram by ID"""
    try:
        workflow = await workflow_generator.get_workflow(workflow_id)
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return workflow
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


