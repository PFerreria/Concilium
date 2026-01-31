const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // File selection
    selectAudioFile: () => ipcRenderer.invoke('select-audio-file'),
    selectDocumentFile: () => ipcRenderer.invoke('select-document-file'),
    selectTemplateFile: () => ipcRenderer.invoke('select-template-file'),

    // File operations
    readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),
    saveFile: (options) => ipcRenderer.invoke('save-file', options),

    // Dialogs
    showMessage: (options) => ipcRenderer.invoke('show-message', options),

    // App info
    getAppVersion: () => ipcRenderer.invoke('get-app-version')
});
