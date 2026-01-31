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

Built with ❤️ for workflow automation