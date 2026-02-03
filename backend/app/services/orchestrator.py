import logging
from pathlib import Path
from typing import Optional, List
import uuid
from datetime import datetime
import json

from app.services.audio_processor import audio_processor
from app.services.ai_analyzer import ai_analyzer
from app.services.workflow_generator import workflow_generator
from app.models.schemas import WorkflowDiagram, WorkflowStep, ProcessingStatus

logger = logging.getLogger(__name__)

class WorkflowOrchestrator:
    """Orchestrates the audio-to-xml workflow"""
    
    async def audio_to_diagram(
        self,
        audio_path: Path,
        file_id: str,
        workflow_name: Optional[str] = None,
        language: Optional[str] = None
    ) -> WorkflowDiagram:
        """
        End-to-end workflow: Audio -> Transcription -> Steps -> XML
        """
        try:
            workflow_id = str(uuid.uuid4())
            name = workflow_name or f"Workflow from {file_id}"
            logger.info(f"Starting audio-to-xml workflow for {file_id} (ID: {workflow_id})")

            # 1. Take the audio and transcribe it
            transcription = await audio_processor.transcribe_audio(
                audio_path, file_id, language
            )
            logger.info(f"Step 1 completed: Transcription done for {file_id}")
            
            if not transcription.full_text.strip():
                raise ValueError("Transcription resulted in empty text")
                
            logger.debug(f"Transcript: {transcription.full_text[:200]}...")

            # 2. From this transcription, analyse which are the steps described
            steps = await ai_analyzer.extract_workflow_from_text(
                transcription.full_text,
                context=f"Generated from audio file {file_id}"
            )
            logger.info(f"Step 2 completed: {len(steps)} steps extracted")

            if not steps:
                logger.error(f"AI Analysis failed. Transcript was: {transcription.full_text}")
                raise ValueError("AI analysis failed to extract any workflow steps")
                
            # Log steps for debugging
            logger.debug(f"Steps: {[s.name for s in steps]}")

            # 3. Convert these steps into a .xml file
            xml_path = await workflow_generator.generate_bpmn_xml(
                workflow_id, steps, name, "Auto-generated from audio transcription"
            )
            logger.info(f"Step 3 completed: XML generated at {xml_path}")

            # Return result with NO diagram path
            return WorkflowDiagram(
                workflow_id=workflow_id,
                name=name,
                description="Auto-generated from audio transcription",
                steps=steps,
                transcript=transcription.full_text,
                xml_path=str(xml_path),
                diagram_path=None, # Explicitly None as requested
                created_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Audio-to-xml workflow failed: {e}")
            raise

# Global instance
workflow_orchestrator = WorkflowOrchestrator()
