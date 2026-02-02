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


@router.post("/analyze/workflow")
async def analyze_workflow(
    text: str,
    workflow_name: str,
    context: Optional[str] = None
):
    try:
        # Extract workflow steps using AI
        steps = await ai_analyzer.extract_workflow_from_text(text, context)
        
        # Generate workflow diagram
        workflow = await workflow_generator.generate_workflow(
            steps, workflow_name, context or ""
        )
        
        return workflow
        
    except Exception as e:
        logger.error(f"Workflow analysis failed: {e}")
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


@router.post("/process", response_model=ProcessResponse)
async def process_all(
    request: ProcessRequest,
    background_tasks: BackgroundTasks
):
    """
    Start an end-to-end processing job
    """
    try:
        job_id = str(uuid.uuid4())
        
        logger.info(f"Starting processing job: {job_id}")
        
        # Initialize job status
        jobs[job_id] = {
            "status": ProcessingStatus.PROCESSING,
            "message": "Processing started"
        }
        
        # Process in background
        background_tasks.add_task(
            process_job,
            job_id,
            request
        )
        
        return ProcessResponse(
            job_id=job_id,
            status=ProcessingStatus.PROCESSING,
            message="Processing started. Use /api/v1/job/{job_id} to check status."
        )
        
    except Exception as e:
        logger.error(f"Process initiation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_job(job_id: str, request: ProcessRequest):
    """Background job for processing"""
    try:
        transcriptions = []
        workflows = []
        completed_documents = []
        
        # Step 1: Transcribe audio files
        if request.audio_file_ids:
            logger.info(f"Job {job_id}: Transcribing {len(request.audio_file_ids)} audio files")
            
            for file_id in request.audio_file_ids:
                # Find audio file
                audio_path = None
                for ext in settings.allowed_audio_formats:
                    potential_path = settings.upload_dir / f"{file_id}{ext}"
                    if potential_path.exists():
                        audio_path = potential_path
                        break
                
                if audio_path:
                    result = await audio_processor.transcribe_audio(audio_path, file_id)
                    transcriptions.append(result)
        
        # Step 2: Process documents
        document_texts = []
        if request.document_file_ids:
            logger.info(f"Job {job_id}: Processing {len(request.document_file_ids)} documents")
            
            for file_id in request.document_file_ids:
                # Find document file
                doc_path = None
                for ext in settings.allowed_document_formats:
                    potential_path = settings.upload_dir / f"{file_id}{ext}"
                    if potential_path.exists():
                        doc_path = potential_path
                        break
                
                if doc_path:
                    result = await document_processor.process_document(doc_path, file_id)
                    document_texts.append(result['text'])
        
        # Combine all text sources
        all_text = "\n\n".join([t.full_text for t in transcriptions] + document_texts)
        
        # Step 3: Generate workflow if requested
        if request.generate_workflow and all_text:
            logger.info(f"Job {job_id}: Generating workflow")
            
            steps = await ai_analyzer.extract_workflow_from_text(all_text)
            workflow = await workflow_generator.generate_workflow(
                steps,
                request.workflow_name or "Generated Workflow",
                "Auto-generated from uploaded files"
            )
            workflows.append(workflow)
        
        # Step 4: Complete templates if requested
        if request.complete_templates and request.template_file_ids and all_text:
            logger.info(f"Job {job_id}: Completing {len(request.template_file_ids)} templates")
            
            for template_id in request.template_file_ids:
                # Find template file
                template_path = None
                for ext in settings.allowed_document_formats:
                    potential_path = settings.template_dir / f"{template_id}{ext}"
                    if potential_path.exists():
                        template_path = potential_path
                        break
                
                if template_path:
                    # Extract template fields
                    fields = await document_processor.extract_template_fields(template_path)
                    
                    # Extract data for fields using AI
                    extracted_data = await ai_analyzer.extract_template_data(all_text, fields)
                    
                    # Fill template
                    completed = await template_filler.fill_template(
                        template_path, extracted_data
                    )
                    completed_documents.append(completed)
        
        # Update job status
        jobs[job_id] = {
            "status": ProcessingStatus.COMPLETED,
            "message": "Processing completed successfully",
            "transcriptions": transcriptions,
            "workflows": workflows,
            "completed_documents": completed_documents
        }
        
        logger.info(f"Job {job_id}: Completed successfully")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        jobs[job_id] = {
            "status": ProcessingStatus.FAILED,
            "message": f"Processing failed: {str(e)}",
            "error": str(e)
        }


@router.get("/job/{job_id}", response_model=ProcessResponse)
async def get_job_status(job_id: str):
    """Get processing job status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = jobs[job_id]
    
    return ProcessResponse(
        job_id=job_id,
        status=job_data["status"],
        message=job_data["message"],
        transcriptions=job_data.get("transcriptions"),
        workflows=job_data.get("workflows"),
        completed_documents=job_data.get("completed_documents"),
        error=job_data.get("error")
    )
