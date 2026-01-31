import whisper
import torch
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from app.config import settings
from app.models.schemas import TranscriptionResult, TranscriptSegment

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Audio processing service using Whisper"""
    
    def __init__(self):
        self.model = None
        self.device = settings.whisper_device
        self._load_model()
    
    def _load_model(self):
        try:
            logger.info(f"Loading Whisper model: {settings.whisper_model_size}")
            self.model = whisper.load_model(
                settings.whisper_model_size,
                device=self.device
            )
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    async def transcribe_audio(
        self,
        audio_path: Path,
        file_id: str,
        language: Optional[str] = None
    ) -> TranscriptionResult:
        """
            logger.info(f"Transcribing audio file: {audio_path}")
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                str(audio_path),
                language=language or settings.whisper_language,
                task="transcribe",
                verbose=False
            )
            
            # Extract segments with timestamps
            segments = []
            for segment in result.get("segments", []):
                segments.append(TranscriptSegment(
                    start_time=segment["start"],
                    end_time=segment["end"],
                    text=segment["text"].strip(),
                    speaker=None  # Can be enhanced with diarization
                ))
            
            # Get full text
            full_text = result.get("text", "").strip()
            
            # Get detected language
            detected_language = result.get("language", "unknown")
            
            # Calculate duration (from last segment)
            duration = segments[-1].end_time if segments else 0.0
            
            transcription = TranscriptionResult(
                file_id=file_id,
                language=detected_language,
                duration_seconds=duration,
                segments=segments,
                full_text=full_text
            )
            
            logger.info(f"Transcription completed: {len(segments)} segments, {duration:.2f}s")
            return transcription
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    async def batch_transcribe(
        self,
        audio_files: List[tuple[Path, str]]
    ) -> List[TranscriptionResult]:
        """
        Transcribe multiple audio files
        
        Args:
            audio_files: List of (audio_path, file_id) tuples
        
        Returns:
            List of transcription results
        """
        results = []
        for audio_path, file_id in audio_files:
            try:
                result = await self.transcribe_audio(audio_path, file_id)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to transcribe {audio_path}: {e}")
                # Continue with other files
        
        return results
    
    def is_ready(self) -> bool:
        """Check if the audio processor is ready"""
        return self.model is not None


# Global instance
audio_processor = AudioProcessor()
