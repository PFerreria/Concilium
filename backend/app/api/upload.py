from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List
import uuid
from pathlib import Path
import logging
import aiofiles

from app.config import settings
from app.models.schemas import (
    AudioUploadResponse,
    DocumentUploadResponse,
    ProcessingStatus,
    FileType
)
from app.services.audio_processor import audio_processor
from app.services.document_processor import document_processor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["uploads"])


def validate_file_size(file: UploadFile) -> bool:
    return True


def validate_audio_format(filename: str) -> bool:
    suffix = Path(filename).suffix.lower()
    return suffix in settings.allowed_audio_formats


def validate_document_format(filename: str) -> bool:
    """Validate document file format"""
    return suffix in settings.allowed_document_formats


@router.post("/upload/audio", response_model=AudioUploadResponse)
async def upload_audio(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
        # Validate format
        if not validate_audio_format(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format. Allowed: {settings.allowed_audio_formats}"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save file
        file_extension = Path(file.filename).suffix
        save_path = settings.upload_dir / f"{file_id}{file_extension}"
        
        async with aiofiles.open(save_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        file_size = len(content)
        
        logger.info(f"Audio file uploaded: {file_id} ({file.filename}, {file_size} bytes)")
        
        return AudioUploadResponse(
            file_id=file_id,
            filename=file.filename,
            size_bytes=file_size,
            status=ProcessingStatus.PENDING,
            message="Audio file uploaded successfully. Use /api/v1/transcribe to process."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/document", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    file_type: FileType = FileType.DOCUMENT
):
    """
    Upload document or template file
    
    Supported formats: pdf, docx, txt, xlsx
    """
    try:
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save file
        file_extension = Path(file.filename).suffix
        
        # Save to appropriate directory
        if file_type == FileType.TEMPLATE:
            save_path = settings.template_dir / f"{file_id}{file_extension}"
        else:
            save_path = settings.upload_dir / f"{file_id}{file_extension}"
        
        async with aiofiles.open(save_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        file_size = len(content)
        
        logger.info(f"Document uploaded: {file_id} ({file.filename}, {file_size} bytes)")
        
        return DocumentUploadResponse(
            file_id=file_id,
            filename=file.filename,
            size_bytes=file_size,
            file_type=file_type,
            status=ProcessingStatus.PENDING,
            message="Document uploaded successfully."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/template", response_model=DocumentUploadResponse)
async def upload_template(file: UploadFile = File(...)):
    """
    Upload document template
    
    Templates should contain placeholders like {{field_name}} or {field_name}
    """
    return await upload_document(file, file_type=FileType.TEMPLATE)


@router.delete("/upload/{file_id}")
async def delete_upload(file_id: str):
        for directory in [settings.upload_dir, settings.template_dir]:
            for file_path in directory.glob(f"{file_id}.*"):
                file_path.unlink()
                found = True
                logger.info(f"Deleted file: {file_id}")
        
        if not found:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {"message": "File deleted successfully", "file_id": file_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
