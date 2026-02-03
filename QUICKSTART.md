# Quick Start Guide - Concilium Desktop App

## For Users (Download and Install)

### Windows
1. Download `Concilium Setup 1.0.0.exe`
2. Run the installer
3. Launch Concilium from Start Menu
4. Go to Settings and set API URL (if not localhost)

### macOS
1. Download `Concilium-1.0.0.dmg`
2. Open the DMG file
3. Drag Concilium to Applications
4. Launch from Applications folder

### Linux
1. Download `Concilium-1.0.0.AppImage`
2. Make it executable: `chmod +x Concilium-1.0.0.AppImage`
3. Run: `./Concilium-1.0.0.AppImage`

## For Developers (Build from Source)

### 1. Install Dependencies

```bash
cd frontend/desktop
npm install
```

### 2. Run in Development

```bash
npm start
```

### 3. Build Installer

```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux

# All platforms
npm run build
```

Installers will be in `dist/` folder.

## Using the App

### 1. Start Backend API

Before using the desktop app, start the Concilium backend:

```bash
cd backend
python -m app.main
```

API runs at: `http://localhost:8000`

### 2. Configure Connection

1. Open Concilium desktop app
2. Click Settings (gear icon or sidebar)
3. Set "API Server URL" to `http://localhost:8000`
4. Click "Test Connection" - should show ✓ Connected

### 3. Process Files

1. Click "Process Files" in sidebar
2. Upload files:
   - **Audio**: Click "Select Audio" → choose MP3/WAV/etc.
   - **Documents**: Click "Select Document" → choose PDF/DOCX
   - **Templates**: Click "Select Template" → choose DOCX with {{placeholders}}
3. Choose options:
   - ✓ Generate Workflow Diagrams
   - ✓ Complete Templates
   - Optional: Enter workflow name
4. Click "Start Processing"
5. Wait for results
6. Click "Download" on any result to save

### 4. View History

Click "History" in sidebar to see past processing jobs.

## Troubleshooting

### "Cannot connect to API"
- Make sure backend is running: `python -m app.main`
- Check API URL in Settings matches where backend is running
- Test connection using "Test Connection" button

### "Processing failed"
- Check backend logs for errors
- Ensure AI models are loaded (check backend startup logs)
- Try with smaller files first

### App won't start
- Windows: Run as administrator
- macOS: Right-click → Open (if security warning)
- Linux: Ensure AppImage is executable

## Features

✅ Upload audio, documents, and templates  
✅ Real-time processing progress  
✅ Download generated workflows (XML + diagrams)  
✅ Download completed documents  
✅ Processing history  
✅ Configurable API endpoint  

## Support

For issues or questions:
- Check backend logs: `backend/logs/concilium.log`
- Check app console: Settings → Help → View Logs
- GitHub Issues: https://github.com/yourusername/Concilium/issues
