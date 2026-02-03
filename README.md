# Concilium AI Assistant

![Concilium Logo](https://via.placeholder.com/150x150/667eea/ffffff?text=Concilium)

**AI-powered workflow generation and document completion assistant**

Concilium automatically transcribes audio, analyzes documents, generates BPMN workflow diagrams, and completes document templates using state-of-the-art open-source AI models.

## 🚀 Features

- **Audio Transcription**: Convert meetings and recordings to text using Whisper AI
- **Document Processing**: Extract content from PDFs, DOCX, and text files
- **Workflow Generation**: Create BPMN 2.0 compliant workflow diagrams automatically
- **Template Completion**: Auto-fill document templates with extracted data
- **API-First Design**: RESTful API for easy integration
- **Open-Source AI**: Uses Llama and Whisper models (no API costs)
- **Flexible Deployment**: Supports both cloud and on-premise installations

## 📋 Prerequisites

- Python 3.9 or higher
- CUDA-capable GPU (recommended for optimal performance)
- 16GB+ RAM
- ffmpeg (for audio processing)

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/Concilium.git
cd Concilium
```

### 2. Set up Python environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install ffmpeg

**Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

**Linux**:
```bash
sudo apt-get install ffmpeg
```

**Mac**:
```bash
brew install ffmpeg
```

### 5. Configure environment

Create a `.env` file in the `backend` directory:

```env
# Application
APP_NAME=Concilium AI Assistant
ENVIRONMENT=development
DEBUG=true

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=true

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# AI Models
LLM_MODEL_NAME=meta-llama/Llama-2-7b-chat-hf
WHISPER_MODEL_SIZE=base
LLM_DEVICE=cuda
WHISPER_DEVICE=cuda

# File Upload
MAX_UPLOAD_SIZE_MB=100

# Database
DATABASE_URL=sqlite+aiosqlite:///./concilium.db

# Logging
LOG_LEVEL=INFO
```

## 🚀 Quick Start

### Start the backend API

```bash
cd backend
python -m app.main
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### View the landing page

Open `frontend/landing/index.html` in your browser or serve it with a simple HTTP server:

```bash
cd frontend/landing
python -m http.server 3000
```

Landing page: `http://localhost:3000`

## 📖 API Usage

### 1. Upload an audio file

```bash
curl -X POST "http://localhost:8000/api/v1/upload/audio" \
  -F "file=@meeting.mp3"
```

Response:
```json
{
  "file_id": "abc123...",
  "filename": "meeting.mp3",
  "status": "pending"
}
```

### 2. Transcribe the audio

```bash
curl -X POST "http://localhost:8000/api/v1/transcribe/abc123"
```

### 3. Generate workflow from transcript

```bash
curl -X POST "http://localhost:8000/api/v1/analyze/workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "First we review the proposal, then we get approval...",
    "workflow_name": "Approval Process"
  }'
```

### 4. End-to-end processing

```bash
curl -X POST "http://localhost:8000/api/v1/process" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_file_ids": ["abc123"],
    "template_file_ids": ["def456"],
    "generate_workflow": true,
    "complete_templates": true
  }'
```

## 🏗️ Project Structure

```
Concilium/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── models/           # Data models
│   │   ├── services/         # Business logic
│   │   │   ├── audio_processor.py
│   │   │   ├── document_processor.py
│   │   │   ├── ai_analyzer.py
│   │   │   ├── workflow_generator.py
│   │   │   └── template_filler.py
│   │   ├── config.py         # Configuration
│   │   └── main.py           # FastAPI app
│   ├── requirements.txt
│   └── tests/
├── frontend/
│   └── landing/              # Landing page
│       ├── index.html
│       ├── styles.css
│       └── script.js
├── docs/
└── README.md
```

## 🔧 Configuration

### AI Models

**Llama Model**: By default uses `Llama-2-7b-chat-hf`. For better performance, consider:
- `Llama-2-13b-chat-hf` (requires more VRAM)
- `Llama-2-70b-chat-hf` (requires multi-GPU setup)

**Whisper Model**: Options are `tiny`, `base`, `small`, `medium`, `large`
- `tiny/base`: Fast, lower accuracy
- `small/medium`: Balanced
- `large`: Best accuracy, slower

### Deployment Options

#### Cloud Deployment
- Deploy to AWS, GCP, or Azure
- Use GPU instances (e.g., AWS p3, GCP A100)
- Set up load balancing for scalability

#### On-Premise Deployment
- Install on local servers
- Configure firewall rules
- Set up SSL certificates

## 🧪 Testing

```bash
cd backend
pytest tests/
```

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [User Guide](docs/USER_GUIDE.md) - How to use Concilium
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Development setup

## 🤝 Integration

### CRM Integration

Concilium can be integrated with popular CRM systems:

**Salesforce**: Create a custom app that calls the Concilium API
**HubSpot**: Use webhooks to trigger workflow generation
**Custom CRM**: Use the REST API for seamless integration

Example integration:
```python
import requests

# Upload and process in your CRM workflow
response = requests.post(
    "http://your-concilium-server/api/v1/process",
    json={
        "audio_file_ids": [audio_id],
        "generate_workflow": True
    }
)
```

## 🔒 Security

- API key authentication (configure in `.env`)
- File size limits
- Input validation
- CORS configuration
- Rate limiting (recommended for production)

## 📈 Performance

- GPU acceleration for AI models
- Async processing for I/O operations
- Background task queue for long-running jobs
- Caching for frequently accessed data

## 🐛 Troubleshooting

### Models not loading
- Check GPU availability: `nvidia-smi`
- Verify CUDA installation
- Try CPU mode: Set `LLM_DEVICE=cpu` and `WHISPER_DEVICE=cpu`

### Out of memory
- Use smaller models (Llama-2-7b, Whisper base)
- Reduce batch sizes
- Enable model quantization

### Slow transcription
- Use GPU acceleration
- Choose smaller Whisper model
- Process shorter audio segments

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Audio transcription
- [Meta Llama](https://ai.meta.com/llama/) - Language model
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Graphviz](https://graphviz.org/) - Diagram generation

## 📞 Support

- Email: support@concilium.ai
- Documentation: https://docs.concilium.ai
- Issues: https://github.com/yourusername/Concilium/issues

---

# Cross-Platform Deployment Guide

## Overview

This guide will help you deploy Concilium on any system (Windows, macOS, Linux) with proper dependency management.

---

## Part 1: System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 11+, Ubuntu 20.04+
- **RAM**: 8GB (16GB recommended for AI models)
- **Storage**: 10GB free space
- **Python**: 3.9 - 3.11
- **Network**: For downloading models on first run

### Optional (Performance)
- NVIDIA GPU with CUDA support (for faster processing)
- CUDA 11.8+ and cuDNN

---

## Part 2: Platform-Specific Setup

### Windows

#### Step 1: Install Python
```powershell
# Download Python 3.11 from python.org
# OR use winget
winget install Python.Python.3.11

# Verify installation
python --version
```

#### Step 2: Install ffmpeg
```powershell
# Option A: Download from https://ffmpeg.org/download.html
# Extract to C:\ffmpeg
# Add C:\ffmpeg\bin to PATH

# Option B: Use Chocolatey
choco install ffmpeg

# Verify
ffmpeg -version
```

#### Step 3: Install Visual C++ Build Tools (for some Python packages)
```powershell
# Download from:
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Install "Desktop development with C++"
```

#### Step 4: Set up Concilium
```powershell
cd Concilium\backend

# Create virtual environment
python -m venv venv

# Activate
.\venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install PyTorch (CPU version for systems without GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# OR for CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

### macOS

#### Step 1: Install Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: Install Dependencies
```bash
# Install Python
brew install python@3.11

# Install ffmpeg
brew install ffmpeg

# Verify
python3 --version
ffmpeg -version
```

#### Step 3: Set up Concilium
```bash
cd Concilium/backend

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install PyTorch for macOS (MPS support for Apple Silicon)
pip install torch torchvision torchaudio
```

---

### Linux (Ubuntu/Debian)

#### Step 1: Update System
```bash
sudo apt update
sudo apt upgrade -y
```

#### Step 2: Install Dependencies
```bash
# Install Python and dev tools
sudo apt install -y python3.11 python3.11-venv python3.11-dev
sudo apt install -y build-essential

# Install ffmpeg
sudo apt install -y ffmpeg

# Install audio libraries
sudo apt install -y portaudio19-dev

# Verify
python3.11 --version
ffmpeg -version
```

#### Step 3: Set up Concilium
```bash
cd Concilium/backend

# Create virtual environment
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install PyTorch (CPU or CUDA)
# CPU version:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# OR CUDA 11.8:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## Part 3: Configuration for Portability

### Create environment configuration

Create `.env` file in `backend/` directory:

```bash
# Application Settings
APP_NAME=Concilium AI Assistant
ENVIRONMENT=production
DEBUG=false

# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=false

# AI Models - Optimized for lower resources
LLM_MODEL_NAME=meta-llama/Llama-2-7b-chat-hf
WHISPER_MODEL_SIZE=base
LLM_DEVICE=cpu
WHISPER_DEVICE=cpu

# Hugging Face Token (required for Llama models)
HF_TOKEN=your_token_here

# File Upload
MAX_UPLOAD_SIZE_MB=100

# Database
DATABASE_URL=sqlite+aiosqlite:///./concilium.db

# Logging
LOG_LEVEL=INFO
```

### Get Hugging Face Token
1. Go to https://huggingface.co/
2. Create account / Sign in
3. Go to Settings → Access Tokens
4. Create new token with "Read" permission
5. Copy token to `.env` file

---

## Part 4: Running the Application

### Start Backend API

```bash
# Windows
cd backend
venv\Scripts\activate
python -m app.main

# macOS/Linux
cd backend
source venv/bin/activate
python -m app.main
```

### Start Desktop App (Optional)

```bash
# Windows
cd frontend\desktop
npm install
npm start

# macOS/Linux
cd frontend/desktop
npm install
npm start
```

---

## Part 5: Docker Deployment (Recommended for Production)

### Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install PyTorch CPU version (smaller image)
RUN pip install --no-cache-dir torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

# Copy application
COPY backend/ .

# Create directories
RUN mkdir -p uploads outputs/workflows outputs/documents templates logs

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "app.main"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  concilium:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HF_TOKEN=${HF_TOKEN}
      - LLM_DEVICE=cpu
      - WHISPER_DEVICE=cpu
    volumes:
      - ./uploads:/app/uploads
      - ./outputs:/app/outputs
      - ./templates:/app/templates
      - ./logs:/app/logs
    restart: unless-stopped
```

### Run with Docker

```bash
# Set HF_TOKEN in .env file or export it
export HF_TOKEN=your_token_here

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Part 6: Optimizations for Different Systems

### Low-Resource Systems (4-8GB RAM)

Update `.env`:
```bash
LLM_MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0
WHISPER_MODEL_SIZE=tiny
LLM_DEVICE=cpu
WHISPER_DEVICE=cpu
```

### GPU Systems (NVIDIA with CUDA)

Update `.env`:
```bash
LLM_DEVICE=cuda
WHISPER_DEVICE=cuda
```

Install CUDA-enabled PyTorch:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Apple Silicon (M1/M2/M3)

Update `.env`:
```bash
LLM_DEVICE=mps
WHISPER_DEVICE=cpu  # Whisper works better on CPU for Mac
```

---

## Part 7: Troubleshooting

### Issue: "CUDA not available" but I have GPU

**Solution:**
```bash
# Reinstall PyTorch with CUDA support
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

### Issue: "ffmpeg not found"

**Windows:**
```powershell
# Add to PATH manually or reinstall
choco install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

### Issue: Models fail to load

**Solution:**
```bash
# Check HF_TOKEN is set
echo $HF_TOKEN  # Linux/Mac
echo %HF_TOKEN%  # Windows

# Accept Llama 2 license at:
# https://huggingface.co/meta-llama/Llama-2-7b-chat-hf

# Try smaller model first
LLM_MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

### Issue: Out of memory errors

**Solution:**
```bash
# Use CPU instead of GPU
LLM_DEVICE=cpu
WHISPER_DEVICE=cpu

# Use smaller models
WHISPER_MODEL_SIZE=tiny
LLM_MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

---

## Part 8: Production Deployment Checklist

- [ ] Use virtual environment
- [ ] Set proper environment variables
- [ ] Use production-grade server (e.g., gunicorn)
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up logging and monitoring
- [ ] Regular backups of outputs/uploads
- [ ] Use Docker for consistency
- [ ] Set DEBUG=false
- [ ] Use strong SECRET_KEY

---

## Part 9: Cloud Deployment Options

### AWS EC2

1. Launch EC2 instance (t3.medium or better)
2. SSH into instance
3. Follow Linux installation steps
4. Configure security groups (port 8000)
5. Use Elastic IP for stable address

### Google Cloud Run (Serverless)

```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/concilium

# Deploy
gcloud run deploy concilium \
  --image gcr.io/PROJECT_ID/concilium \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Container Instances

```bash
# Build and push to ACR
az acr build --registry myregistry --image concilium .

# Deploy
az container create \
  --resource-group mygroup \
  --name concilium \
  --image myregistry.azurecr.io/concilium \
  --ports 8000
```

---

## Part 10: Performance Benchmarks

| System | Model Size | Processing Time (1min audio) |
|--------|-----------|------------------------------|
| CPU (Intel i5) | Whisper base | ~30s |
| CPU (Intel i5) | Whisper tiny | ~10s |
| GPU (RTX 3060) | Whisper base | ~5s |
| M1 Mac | Whisper base | ~15s |

---

## Support

For additional help:
- Check logs: `backend/logs/concilium.log`
- GitHub Issues: https://github.com/yourusername/Concilium/issues
- Documentation: README.md