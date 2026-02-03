# 🎨 Diagram Generation - Quick Reference

## What Changed

Your Concilium system now generates **visual workflow diagrams** automatically! 

### Before
- ✅ Audio → Transcript → BPMN XML

### After  
- ✅ Audio → Transcript → BPMN XML **+ Visual Diagram** 📊

---

## Installation (Quick)

### 1. Install Graphviz

```bash
# Windows
choco install graphviz

# macOS
brew install graphviz

# Linux
sudo apt install graphviz
```

### 2. Update Dependencies

```bash
cd backend
pip install graphviz matplotlib networkx pillow
```

### 3. Replace Files

**Backend:**
- Replace: `backend/app/services/workflow_generator.py`
- With: `workflow_generator_with_diagrams.py`

**Frontend (optional):**
- Replace: `frontend/desktop/renderer/app.js`
- With: `app_with_diagram_support.js`

### 4. Restart Application

```bash
cd backend
python -m app.main
```

---

## Usage

### Desktop App

1. Upload audio → Process
2. Get 3 files:
   - 📝 Transcript (txt)
   - 📄 BPMN XML (xml)
   - 🖼️ **Diagram (png/svg/pdf)** ← NEW!
3. Click **Preview** to view diagram
4. Click **Download** to save

### API

```bash
# Upload and process
curl -X POST "http://localhost:8000/api/v1/workflow/audio?file_id=FILE_ID"

# Response now includes:
{
  "xml_path": "...",
  "diagram_path": "..."  ← NEW!
}

# Download diagram
curl "http://localhost:8000/download/workflow/ID/diagram" -o diagram.png
```

---

## Features

✅ **Professional BPMN-style diagrams**  
✅ **Color-coded elements:**
   - 🟢 Start events (green)
   - 🔴 End events (red)
   - 🔵 Tasks (blue)
   - 🟡 Gateways (yellow)

✅ **Multiple formats:** PNG, SVG, PDF  
✅ **Automatic fallback** if Graphviz not installed  
✅ **Preview in desktop app**  

---

## File Structure

```
Delivered Files:
├── workflow_generator_with_diagrams.py  ← Replace workflow_generator.py
├── requirements_with_diagrams.txt       ← New requirements
├── app_with_diagram_support.js         ← Replace app.js (frontend)
└── DIAGRAM_GENERATION_SETUP.md         ← Full guide
```

---

## Troubleshooting

### No diagram generated?

1. Check Graphviz: `dot -V`
2. Check logs: `tail -f backend/logs/concilium.log`
3. Reinstall Graphviz if needed

### "dot: command not found"?

**Graphviz not in PATH:**
```bash
# Windows: Add C:\Program Files\Graphviz\bin to PATH
# Mac/Linux: Reinstall graphviz
```

---

## Configuration

Edit `backend/.env`:
```bash
DIAGRAM_FORMAT=png  # Options: png, svg, pdf
```

---

## Example Output

### Before (2 files):
```
workflow_abc123.xml
transcript_abc123.txt
```

### After (3 files):
```
workflow_abc123.xml
workflow_abc123.png  ← NEW!
transcript_abc123.txt
```

---

## Next Steps

1. ✅ Install Graphviz
2. ✅ Update Python dependencies  
3. ✅ Replace workflow_generator.py
4. ✅ (Optional) Update desktop app
5. ✅ Test with audio file
6. ✅ View beautiful diagrams!

---

## Full Documentation

See `DIAGRAM_GENERATION_SETUP.md` for:
- Detailed installation steps
- Platform-specific guides
- Advanced customization
- Troubleshooting
- Docker support
- Performance notes

---

## Support

Questions? Check:
1. DIAGRAM_GENERATION_SETUP.md (detailed guide)
2. backend/logs/concilium.log (error logs)
3. This quick reference (common issues)

Enjoy your visual workflows! 🎉
