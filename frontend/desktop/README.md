# Concilium Desktop Application

## Build and Run Instructions

### Prerequisites

- Node.js 16+ installed
- Backend API running (see backend README)

### Installation

```bash
cd frontend/desktop
npm install
```

### Development

Run the app in development mode:

```bash
npm start
```

Or with DevTools open:

```bash
npm run dev
```

### Building Installers

#### Windows

```bash
npm run build:win
```

This creates:
- `dist/Concilium Setup 1.0.0.exe` - Installer
- `dist/Concilium 1.0.0.exe` - Portable version

#### macOS

```bash
npm run build:mac
```

This creates:
- `dist/Concilium-1.0.0.dmg` - DMG installer
- `dist/Concilium-1.0.0-mac.zip` - ZIP archive

#### Linux

```bash
npm run build:linux
```

This creates:
- `dist/Concilium-1.0.0.AppImage` - AppImage
- `dist/concilium_1.0.0_amd64.deb` - Debian package

### All Platforms

```bash
npm run build
```

## Configuration

### API Server

The app connects to your Concilium backend API. Default: `http://localhost:8000`

To change:
1. Open the app
2. Go to Settings
3. Update "API Server URL"
4. Click "Test Connection"

### Icons

Place your app icons in `assets/`:
- `icon.png` - Linux (512x512 PNG)
- `icon.ico` - Windows (256x256 ICO)
- `icon.icns` - macOS (ICNS file)

## Features

### File Upload
- Select audio files (MP3, WAV, M4A, OGG, FLAC)
- Select documents (PDF, DOCX, TXT, XLSX)
- Select templates (DOCX, TXT)

### Processing
- Transcribe audio files
- Generate workflow diagrams
- Complete document templates
- Real-time progress tracking

### Results
- Download generated workflows (XML + diagrams)
- Download completed documents
- View processing history

### Settings
- Configure API server URL
- Test connection to backend
- View app version

## Distribution

After building, distribute the installers:

**Windows**: Share the `.exe` installer or portable `.exe`
**macOS**: Share the `.dmg` file
**Linux**: Share the `.AppImage` or `.deb` package

## Troubleshooting

### App won't start
- Check Node.js version: `node --version` (should be 16+)
- Reinstall dependencies: `rm -rf node_modules && npm install`

### Can't connect to API
- Ensure backend is running: `python -m app.main`
- Check API URL in Settings
- Test connection using "Test Connection" button

### Build fails
- Clear cache: `npm run build -- --clean`
- Check disk space
- Ensure you have write permissions to `dist/` folder

## Development Notes

### Project Structure

```
frontend/desktop/
├── main.js           # Electron main process
├── preload.js        # Preload script (IPC bridge)
├── renderer/         # UI files
│   ├── index.html    # Main UI
│   ├── styles.css    # Styling
│   └── app.js        # Application logic
├── assets/           # Icons and resources
└── package.json      # Dependencies and build config
```

### Adding Features

1. **UI**: Edit `renderer/index.html` and `renderer/styles.css`
2. **Logic**: Edit `renderer/app.js`
3. **IPC**: Add handlers in `main.js` and expose in `preload.js`

### Security

- Context isolation enabled
- Node integration disabled
- Preload script for secure IPC
- No eval() or remote code execution

## License

MIT License - see root LICENSE file
