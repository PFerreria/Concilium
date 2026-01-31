const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, 'assets', 'icon.png'),
        backgroundColor: '#0a0e27',
        titleBarStyle: 'default',
        show: false
    });

    mainWindow.loadFile('renderer/index.html');

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    // Open DevTools in development
    if (process.argv.includes('--dev')) {
        mainWindow.webContents.openDevTools();
    }

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// IPC Handlers

// Select audio file
ipcMain.handle('select-audio-file', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openFile'],
        filters: [
            { name: 'Audio Files', extensions: ['mp3', 'wav', 'm4a', 'ogg', 'flac'] }
        ]
    });

    if (!result.canceled && result.filePaths.length > 0) {
        const filePath = result.filePaths[0];
        return {
            path: filePath,
            name: path.basename(filePath),
            size: fs.statSync(filePath).size
        };
    }
    return null;
});

// Select document file
ipcMain.handle('select-document-file', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openFile'],
        filters: [
            { name: 'Documents', extensions: ['pdf', 'docx', 'txt', 'xlsx'] }
        ]
    });

    if (!result.canceled && result.filePaths.length > 0) {
        const filePath = result.filePaths[0];
        return {
            path: filePath,
            name: path.basename(filePath),
            size: fs.statSync(filePath).size
        };
    }
    return null;
});

// Select template file
ipcMain.handle('select-template-file', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openFile'],
        filters: [
            { name: 'Templates', extensions: ['docx', 'txt'] }
        ]
    });

    if (!result.canceled && result.filePaths.length > 0) {
        const filePath = result.filePaths[0];
        return {
            path: filePath,
            name: path.basename(filePath),
            size: fs.statSync(filePath).size
        };
    }
    return null;
});

// Read file as buffer
ipcMain.handle('read-file', async (event, filePath) => {
    try {
        const buffer = fs.readFileSync(filePath);
        return buffer;
    } catch (error) {
        console.error('Error reading file:', error);
        throw error;
    }
});

// Save file
ipcMain.handle('save-file', async (event, { defaultPath, data }) => {
    const result = await dialog.showSaveDialog(mainWindow, {
        defaultPath: defaultPath,
        filters: [
            { name: 'All Files', extensions: ['*'] }
        ]
    });

    if (!result.canceled && result.filePath) {
        fs.writeFileSync(result.filePath, Buffer.from(data));
        return result.filePath;
    }
    return null;
});

// Show message dialog
ipcMain.handle('show-message', async (event, { type, title, message }) => {
    await dialog.showMessageBox(mainWindow, {
        type: type || 'info',
        title: title || 'Concilium',
        message: message
    });
});

// Get app version
ipcMain.handle('get-app-version', () => {
    return app.getVersion();
});
