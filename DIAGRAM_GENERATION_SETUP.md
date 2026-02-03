# Diagram Generation Setup Guide

## Overview

The enhanced Concilium system now generates **visual workflow diagrams** in addition to BPMN XML files. This guide explains how to set up and use the diagram generation feature.

---

## What's New

✅ **Automatic Diagram Generation**: Every workflow now includes a visual diagram  
✅ **Multiple Rendering Methods**: Uses Graphviz (primary) or Matplotlib (fallback)  
✅ **Multiple Formats**: PNG, SVG, or PDF diagrams  
✅ **Preview in Desktop App**: View diagrams before downloading  
✅ **Download & Share**: Get both XML and visual diagram files  

---

## Installation Steps

### Step 1: Install System Dependencies

The diagram generation feature requires **Graphviz** to be installed on your system.

#### Windows

**Option A: Chocolatey (Recommended)**
```powershell
choco install graphviz
```

**Option B: Manual Download**
1. Download from https://graphviz.org/download/
2. Install to `C:\Program Files\Graphviz`
3. Add to PATH:
   - Open "Environment Variables"
   - Add `C:\Program Files\Graphviz\bin` to PATH
   - Restart terminal

**Verify Installation:**
```powershell
dot -V
# Should output: dot - graphviz version X.X.X
```

#### macOS

```bash
brew install graphviz
```

**Verify Installation:**
```bash
dot -V
# Should output: dot - graphviz version X.X.X
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install graphviz
```

**Verify Installation:**
```bash
dot -V
# Should output: dot - graphviz version X.X.X
```

#### Linux (RHEL/CentOS/Fedora)

```bash
sudo yum install graphviz
# OR
sudo dnf install graphviz
```

---

### Step 2: Update Python Dependencies

Replace your `requirements.txt` with the new version that includes diagram libraries:

```bash
cd backend

# Backup old requirements (optional)
cp requirements.txt requirements.txt.backup

# Use new requirements file
cp path/to/requirements_with_diagrams.txt requirements.txt

# Reinstall dependencies
pip install -r requirements.txt
```

**New dependencies added:**
- `graphviz>=0.20.1` - Primary diagram renderer
- `matplotlib>=3.8.0` - Fallback renderer
- `networkx>=3.2.1` - Graph layout algorithms
- `pillow>=10.1.0` - Image processing

---

### Step 3: Replace Workflow Generator

Replace the old workflow generator with the new version:

```bash
cd backend/app/services

# Backup old file (optional)
cp workflow_generator.py workflow_generator.py.backup

# Replace with new version
cp path/to/workflow_generator_with_diagrams.py workflow_generator.py
```

---

### Step 4: Update Desktop App (Optional)

If using the desktop application, update the frontend:

```bash
cd frontend/desktop/renderer

# Backup old file
cp app.js app.js.backup

# Replace with new version
cp path/to/app_with_diagram_support.js app.js
```

The updated app includes:
- Diagram preview functionality
- Download support for diagram files
- Visual feedback for diagram availability

---

### Step 5: Configure Diagram Format

Edit `backend/.env` to set your preferred diagram format:

```bash
# Options: png, svg, pdf
DIAGRAM_FORMAT=png
```

**Format Recommendations:**
- **PNG**: Best for embedding in documents, universal compatibility
- **SVG**: Best for scaling, editing, web display
- **PDF**: Best for printing, professional documents

---

## Testing the Feature

### Test 1: Verify Graphviz

```bash
python -c "from graphviz import Digraph; print('Graphviz OK')"
```

**Expected output:** `Graphviz OK`

**If error:** Check Graphviz installation and PATH

### Test 2: Generate a Test Diagram

```bash
cd backend
python -c "
from app.services.workflow_generator import workflow_generator
from app.models.schemas import WorkflowStep
import asyncio

steps = [
    WorkflowStep(step_id='s1', name='Start', description='', step_type='event', next_steps=['s2']),
    WorkflowStep(step_id='s2', name='Process', description='Main task', step_type='task', next_steps=['s3']),
    WorkflowStep(step_id='s3', name='End', description='', step_type='event', next_steps=[])
]

async def test():
    result = await workflow_generator.generate_workflow(steps, 'Test Workflow')
    print(f'XML: {result.xml_path}')
    print(f'Diagram: {result.diagram_path}')

asyncio.run(test())
"
```

**Expected output:**
```
XML: outputs/workflows/workflow_XXXXX.xml
Diagram: outputs/workflows/workflow_XXXXX.png
```

### Test 3: End-to-End Test

1. Start the backend:
```bash
cd backend
python -m app.main
```

2. Upload an audio file via API or desktop app

3. Check the outputs directory:
```bash
ls -la outputs/workflows/
```

**Expected files:**
- `workflow_XXXXX.xml` (BPMN XML)
- `workflow_XXXXX.png` (Diagram image)

---

## How It Works

### Rendering Priority

1. **Graphviz** (Primary)
   - Best quality diagrams
   - Professional BPMN-style layout
   - Requires Graphviz installed
   - Used if available

2. **Matplotlib + NetworkX** (Fallback)
   - Works without Graphviz
   - Good quality, different style
   - Python-only dependencies
   - Automatically used if Graphviz fails

### Diagram Features

**Visual Elements:**
- ✅ Start events (green circles)
- ✅ End events (red double circles)
- ✅ Tasks (blue rounded rectangles)
- ✅ Gateways (yellow diamonds)
- ✅ Flow connections (arrows)

**Layout:**
- Left-to-right flow
- Automatic positioning
- Clear labeling
- Connection arrows

---

## Usage Examples

### Via Desktop App

1. Upload audio file
2. Click "Start Processing"
3. Wait for completion
4. See three result cards:
   - **Transcript** (text file)
   - **BPMN XML** (workflow definition)
   - **Workflow Diagram** (visual representation)
5. Click "Preview" to view diagram
6. Click "Download" to save locally

### Via API

```bash
# Upload audio
curl -X POST "http://localhost:8000/api/v1/upload/audio" \
  -F "file=@meeting.mp3"

# Generate workflow
curl -X POST "http://localhost:8000/api/v1/workflow/audio?file_id=FILE_ID"

# Response includes diagram_path:
{
  "workflow_id": "abc-123",
  "xml_path": "outputs/workflows/workflow_abc-123.xml",
  "diagram_path": "outputs/workflows/workflow_abc-123.png"
}

# Download diagram
curl "http://localhost:8000/download/workflow/abc-123/diagram" \
  --output workflow.png
```

---

## Troubleshooting

### Issue: "No diagram generated"

**Check logs:**
```bash
tail -f backend/logs/concilium.log
```

**Common causes:**
1. Graphviz not installed → Install Graphviz
2. Graphviz not in PATH → Add to PATH and restart
3. Both renderers failed → Check logs for specific error

**Solution:**
```bash
# Verify Graphviz
dot -V

# If not found, reinstall:
# Windows: choco install graphviz
# macOS: brew install graphviz
# Linux: sudo apt install graphviz
```

### Issue: "ImportError: No module named 'graphviz'"

**Solution:**
```bash
pip install graphviz matplotlib networkx pillow
```

### Issue: "Diagram is blank or malformed"

**Possible causes:**
- Empty workflow steps
- Circular dependencies

**Solution:**
Check the input steps and ensure valid workflow structure

### Issue: "FileNotFoundError: [Errno 2] No such file or directory: 'dot'"

This means Graphviz binary is not in PATH.

**Windows Solution:**
```powershell
# Add to PATH
setx PATH "%PATH%;C:\Program Files\Graphviz\bin"
# Restart terminal
```

**Linux/Mac Solution:**
```bash
# Check installation
which dot

# If not found, reinstall
# macOS: brew install graphviz
# Linux: sudo apt install graphviz
```

---

## Customization

### Change Diagram Format

Edit `backend/.env`:
```bash
DIAGRAM_FORMAT=svg  # Options: png, svg, pdf
```

### Customize Colors

Edit `workflow_generator.py`, find the diagram generation section:

```python
# In _generate_graphviz_diagram method
dot.node(step.step_id, step.name, 
         shape='box', 
         fillcolor='YOUR_COLOR')  # Change this
```

**Available colors:**
- Standard: `lightblue`, `lightgreen`, `lightcoral`, `lightyellow`
- Hex codes: `#667eea`, `#764ba2`, etc.
- RGB: `"#FF5733"`

### Customize Layout

```python
# Change layout direction
dot.attr(rankdir='TB')  # Top to bottom
# Options: LR (left-right), RL (right-left), TB (top-bottom), BT (bottom-top)
```

---

## Performance Notes

### Diagram Generation Time

| Workflow Size | Graphviz | Matplotlib |
|--------------|----------|------------|
| 1-5 steps    | <1s      | <1s        |
| 6-15 steps   | 1-2s     | 2-3s       |
| 16-30 steps  | 2-3s     | 4-6s       |
| 31+ steps    | 3-5s     | 6-10s      |

### Resource Usage

- **Memory**: +50-100MB per diagram generation
- **CPU**: Brief spike during rendering
- **Disk**: PNG ~100KB, SVG ~50KB, PDF ~200KB per diagram

---

## Docker Support

The Dockerfile has been updated to include Graphviz:

```dockerfile
# Install Graphviz
RUN apt-get update && apt-get install -y \
    graphviz \
    && rm -rf /var/lib/apt/lists/*
```

No additional steps needed for Docker deployment.

---

## What's Next

Planned enhancements:
- [ ] Interactive diagram editing
- [ ] Custom color schemes
- [ ] Multiple layout algorithms
- [ ] Export to additional formats (SVG animations, interactive HTML)
- [ ] Diagram comparison tool

---

## Support

For issues:
1. Check this guide's Troubleshooting section
2. Review `backend/logs/concilium.log`
3. Verify Graphviz installation: `dot -V`
4. Create GitHub issue with logs and error details

---

## Summary Checklist

- [ ] Graphviz installed and in PATH
- [ ] Python dependencies updated
- [ ] Workflow generator replaced
- [ ] Desktop app updated (if using)
- [ ] Test diagram generation working
- [ ] Preferred format configured in `.env`

Once all steps are complete, your workflows will include beautiful visual diagrams! 🎨
