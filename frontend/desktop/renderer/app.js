// Application State
const state = {
    apiUrl: localStorage.getItem('apiUrl') || 'http://localhost:8000',
    audioFiles: [],
    documentFiles: [],
    templateFiles: [],
    processing: false,
    history: JSON.parse(localStorage.getItem('history') || '[]')
};

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    initializeNavigation();
    initializeFileUploads();
    initializeProcessing();
    initializeSettings();
    loadHistory();

    // Load app version
    const version = await window.electronAPI.getAppVersion();
    document.getElementById('appVersion').textContent = version;
});

// Navigation
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const viewName = item.dataset.view;
            switchView(viewName);

            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

function switchView(viewName) {
    const views = document.querySelectorAll('.view');
    views.forEach(view => view.classList.remove('active'));

    const targetView = document.getElementById(`${viewName}View`);
    if (targetView) {
        targetView.classList.add('active');
    }
}

// File Uploads
function initializeFileUploads() {
    document.getElementById('uploadAudioBtn').addEventListener('click', () => selectFile('audio'));
    document.getElementById('uploadDocumentBtn').addEventListener('click', () => selectFile('document'));
    document.getElementById('uploadTemplateBtn').addEventListener('click', () => selectFile('template'));
}

async function selectFile(type) {
    let fileInfo;

    switch (type) {
        case 'audio':
            fileInfo = await window.electronAPI.selectAudioFile();
            if (fileInfo) {
                state.audioFiles.push(fileInfo);
                updateFileList('audio');
            }
            break;
        case 'document':
            fileInfo = await window.electronAPI.selectDocumentFile();
            if (fileInfo) {
                state.documentFiles.push(fileInfo);
                updateFileList('document');
            }
            break;
        case 'template':
            fileInfo = await window.electronAPI.selectTemplateFile();
            if (fileInfo) {
                state.templateFiles.push(fileInfo);
                updateFileList('template');
            }
            break;
    }

    updateProcessButton();
}

function updateFileList(type) {
    const listId = `${type}FileList`;
    const list = document.getElementById(listId);
    const files = type === 'audio' ? state.audioFiles :
        type === 'document' ? state.documentFiles :
            state.templateFiles;

    list.innerHTML = files.map((file, index) => `
        <div class="file-item">
            <div class="file-item-info">
                <div class="file-item-name">${file.name}</div>
                <div class="file-item-size">${formatFileSize(file.size)}</div>
            </div>
            <button class="file-item-remove" onclick="removeFile('${type}', ${index})">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </button>
        </div>
    `).join('');
}

function removeFile(type, index) {
    if (type === 'audio') {
        state.audioFiles.splice(index, 1);
    } else if (type === 'document') {
        state.documentFiles.splice(index, 1);
    } else {
        state.templateFiles.splice(index, 1);
    }

    updateFileList(type);
    updateProcessButton();
}

function updateProcessButton() {
    // Only check for audio files
    const hasFiles = state.audioFiles.length > 0;
    document.getElementById('processBtn').disabled = !hasFiles;
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Processing
function initializeProcessing() {
    document.getElementById('processBtn').addEventListener('click', startProcessing);
}

async function startProcessing() {
    if (state.processing) return;

    state.processing = true;
    document.getElementById('processBtn').disabled = true;

    // Show progress
    document.getElementById('progressSection').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';

    try {
        // Step 1: Upload files
        updateProgress(10, 'Uploading audio files...');

        const audioFileIds = await uploadFiles(state.audioFiles, 'audio');

        if (audioFileIds.length === 0) {
            throw new Error("No audio files uploaded");
        }

        updateProgress(30, 'Files uploaded. Starting workflow generation...');

        // Step 2: Process each audio file
        const workflowName = document.getElementById('workflowName').value;
        const results = {
            transcriptions: [],
            workflows: [],
            completed_documents: []
        };

        // Process sequentially
        for (let i = 0; i < audioFileIds.length; i++) {
            const fileId = audioFileIds[i];
            updateProgress(30 + ((i / audioFileIds.length) * 60), `Processing file ${i + 1}/${audioFileIds.length}...`);

            // Call orchestrator endpoint
            const url = new URL(`${state.apiUrl}/api/v1/workflow/audio`);
            url.searchParams.append('file_id', fileId);
            if (workflowName) {
                url.searchParams.append('workflow_name', workflowName);
            }

            const processResponse = await fetch(url, {
                method: 'POST'
            });

            if (!processResponse.ok) {
                const error = await processResponse.json();
                throw new Error(error.detail || 'Workflow generation failed');
            }

            const workflow = await processResponse.json();
            results.workflows.push(workflow);
        }

        updateProgress(100, 'Processing complete!');

        // Show results
        setTimeout(() => {
            displayResults(results);
            saveToHistory(results);
            resetForm();
        }, 500);

    } catch (error) {
        console.error('Processing error:', error);
        await window.electronAPI.showMessage({
            type: 'error',
            title: 'Processing Error',
            message: `Failed to process files: ${error.message}`
        });
        document.getElementById('progressSection').style.display = 'none';
    } finally {
        state.processing = false;
        updateProcessButton();
    }
}

async function uploadFiles(files, type) {
    const fileIds = [];

    for (const file of files) {
        const buffer = await window.electronAPI.readFile(file.path);
        const blob = new Blob([buffer]);

        const formData = new FormData();
        formData.append('file', blob, file.name);

        const endpoint = type === 'template' ? 'template' : type;
        const response = await fetch(`${state.apiUrl}/api/v1/upload/${endpoint}`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        fileIds.push(data.file_id);
    }

    return fileIds;
}

function updateProgress(percent, text) {
    document.getElementById('progressFill').style.width = `${percent}%`;
    document.getElementById('progressText').textContent = text;
}

function displayResults(results) {
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';

    const resultsGrid = document.getElementById('resultsGrid');
    resultsGrid.innerHTML = '';

    // Display workflows (XML + Diagram + Transcript)
    if (results.workflows && results.workflows.length > 0) {
        results.workflows.forEach(workflow => {
            // Transcript Card
            if (workflow.transcript) {
                resultsGrid.innerHTML += createResultCard(
                    'Audio Transcript',
                    `${workflow.transcript.substring(0, 100)}...`,
                    workflow.workflow_id,
                    'transcript',
                    workflow.transcript
                );
            }

            // XML Card
            resultsGrid.innerHTML += createResultCard(
                'BPMN XML Workflow',
                `Generated from ${workflow.name}`,
                workflow.workflow_id,
                'xml'
            );

            // Diagram Card (if available)
            if (workflow.diagram_path) {
                resultsGrid.innerHTML += createResultCard(
                    'Workflow Diagram',
                    `Visual representation of ${workflow.name}`,
                    workflow.workflow_id,
                    'diagram'
                );
            }
        });
    }

    // Display completed documents
    if (results.completed_documents && results.completed_documents.length > 0) {
        results.completed_documents.forEach(doc => {
            resultsGrid.innerHTML += createResultCard(
                'Completed Document',
                doc.template_name,
                doc.document_id,
                'document'
            );
        });
    }
}

function createResultCard(title, description, id, type, content = null) {
    const downloadAction = content
        ? `downloadLocal('${id}', '${type}', \`${content.replace(/`/g, '\\`').replace(/'/g, "\\'")}\`)`
        : `downloadResult('${id}', '${type}')`;

    const previewButton = type === 'diagram' 
        ? `<button class="btn-secondary" onclick="previewDiagram('${id}')">
             <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                 <path d="M1 8C1 8 3 3 8 3C13 3 15 8 15 8C15 8 13 13 8 13C3 13 1 8 1 8Z" stroke="currentColor" stroke-width="1.5"/>
                 <circle cx="8" cy="8" r="2" stroke="currentColor" stroke-width="1.5"/>
             </svg>
             Preview
           </button>`
        : '';

    return `
        <div class="result-card">
            <div class="result-info">
                <h4>${title}</h4>
                <p>${description}</p>
            </div>
            <div class="result-actions">
                ${previewButton}
                <button class="btn-secondary" onclick="${downloadAction}">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M8 2V10M8 10L5 7M8 10L11 7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                        <path d="M2 12V14H14V12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    </svg>
                    Download
                </button>
            </div>
        </div>
    `;
}

async function previewDiagram(workflowId) {
    try {
        const url = `${state.apiUrl}/download/workflow/${workflowId}/diagram`;
        const response = await fetch(url);
        const blob = await response.blob();
        
        // Create object URL for preview
        const objectUrl = URL.createObjectURL(blob);
        
        // Open in new window
        const previewWindow = window.open('', '_blank', 'width=800,height=600');
        previewWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Workflow Diagram Preview</title>
                <style>
                    body {
                        margin: 0;
                        padding: 20px;
                        background: #0a0e27;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                    }
                    img {
                        max-width: 100%;
                        max-height: 90vh;
                        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
                        border-radius: 8px;
                    }
                </style>
            </head>
            <body>
                <img src="${objectUrl}" alt="Workflow Diagram" />
            </body>
            </html>
        `);
        
        // Clean up object URL after window loads
        previewWindow.addEventListener('load', () => {
            setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
        });
        
    } catch (error) {
        console.error('Preview error:', error);
        await window.electronAPI.showMessage({
            type: 'error',
            title: 'Preview Error',
            message: `Failed to preview diagram: ${error.message}`
        });
    }
}

function downloadLocal(id, type, content) {
    try {
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `transcript_${id}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Download error:', error);
    }
}

async function downloadResult(id, type) {
    try {
        let url;
        let filename;

        if (type === 'xml') {
            url = `${state.apiUrl}/download/workflow/${id}/xml`;
            filename = `workflow_${id}.xml`;
        } else if (type === 'diagram') {
            url = `${state.apiUrl}/download/workflow/${id}/diagram`;
            // Get file extension from settings or default to png
            filename = `workflow_${id}.png`;
        } else if (type === 'document') {
            url = `${state.apiUrl}/download/document/${id}`;
            filename = `document_${id}.docx`;
        } else {
            return;
        }

        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Download failed: ${response.statusText}`);
        }
        
        const blob = await response.blob();
        const arrayBuffer = await blob.arrayBuffer();

        const savedPath = await window.electronAPI.saveFile({
            defaultPath: filename,
            data: arrayBuffer
        });

        if (savedPath) {
            await window.electronAPI.showMessage({
                type: 'info',
                title: 'Download Complete',
                message: `File saved to: ${savedPath}`
            });
        }
    } catch (error) {
        console.error('Download error:', error);
        await window.electronAPI.showMessage({
            type: 'error',
            title: 'Download Error',
            message: `Failed to download file: ${error.message}`
        });
    }
}

function resetForm() {
    state.audioFiles = [];
    state.documentFiles = [];
    state.templateFiles = [];

    updateFileList('audio');
    updateFileList('document');
    updateFileList('template');

    document.getElementById('workflowName').value = '';
    updateProcessButton();
}

// History
function saveToHistory(results) {
    const historyItem = {
        timestamp: new Date().toISOString(),
        results: results
    };

    state.history.unshift(historyItem);

    // Keep only last 50 items
    if (state.history.length > 50) {
        state.history = state.history.slice(0, 50);
    }

    localStorage.setItem('history', JSON.stringify(state.history));
    loadHistory();
}

function loadHistory() {
    const historyList = document.getElementById('historyList');

    if (state.history.length === 0) {
        historyList.innerHTML = '<p class="empty-state">No processing history yet</p>';
        return;
    }

    historyList.innerHTML = state.history.map((item, index) => {
        const date = new Date(item.timestamp);
        const workflowCount = item.results.workflows?.length || 0;
        const docCount = item.results.completed_documents?.length || 0;

        return `
            <div class="history-item">
                <div class="history-header">
                    <h3>Processing Job</h3>
                    <span class="history-date">${date.toLocaleString()}</span>
                </div>
                <div class="history-details">
                    ${workflowCount} workflow(s), ${docCount} document(s)
                </div>
            </div>
        `;
    }).join('');
}

// Settings
function initializeSettings() {
    const apiUrlInput = document.getElementById('apiUrl');
    apiUrlInput.value = state.apiUrl;

    apiUrlInput.addEventListener('change', (e) => {
        state.apiUrl = e.target.value;
        localStorage.setItem('apiUrl', state.apiUrl);
    });

    document.getElementById('testConnectionBtn').addEventListener('click', testConnection);
}

async function testConnection() {
    const statusEl = document.getElementById('connectionStatus');
    statusEl.textContent = 'Testing connection...';
    statusEl.className = 'connection-status';

    try {
        const response = await fetch(`${state.apiUrl}/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            statusEl.textContent = `✓ Connected successfully! Models: Whisper ${data.models_loaded.whisper ? '✓' : '✗'}, Llama ${data.models_loaded.llama ? '✓' : '✗'}`;
            statusEl.className = 'connection-status success';
        } else {
            statusEl.textContent = '✗ Server responded but status is not healthy';
            statusEl.className = 'connection-status error';
        }
    } catch (error) {
        statusEl.textContent = `✗ Connection failed: ${error.message}`;
        statusEl.className = 'connection-status error';
    }
}
