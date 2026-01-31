from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    app_name: str = "Concilium AI Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"  # development, staging, production
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # Security
    secret_key: str = "change-this-secret-key-in-production"
    api_key_header: str = "X-API-Key"
    allowed_origins: List[str] = ["*"]
    
    # File Upload
    max_upload_size_mb: int = 100
    upload_dir: Path = Path("uploads")
    allowed_audio_formats: List[str] = [".mp3", ".wav", ".m4a", ".ogg", ".flac"]
    allowed_document_formats: List[str] = [".pdf", ".docx", ".txt", ".xlsx"]
    
    # AI Models - Open Source
    llm_model_name: str = "meta-llama/Llama-2-7b-chat-hf"
    llm_model_path: Optional[Path] = None  # For local model files
    llm_max_tokens: int = 2048
    llm_temperature: float = 0.7
    llm_device: str = "cuda"  # cuda, cpu, mps
    
    # Whisper Configuration
    whisper_model_size: str = "base"  # tiny, base, small, medium, large
    whisper_device: str = "cuda"  # cuda, cpu
    whisper_language: Optional[str] = None  # Auto-detect if None
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./concilium.db"
    
    # Redis (for background tasks)
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Workflow Generation
    workflow_output_dir: Path = Path("outputs/workflows")
    diagram_format: str = "png"  # png, svg, pdf
    
    # Template Processing
    template_dir: Path = Path("templates")
    output_dir: Path = Path("outputs/documents")
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = Path("logs/concilium.log")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.workflow_output_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
