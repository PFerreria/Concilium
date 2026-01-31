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
    const hasFiles = state.audioFiles.length > 0 ||
        state.documentFiles.length > 0 ||
        state.templateFiles.length > 0;

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
        updateProgress(10, 'Uploading files...');

        const audioFileIds = await uploadFiles(state.audioFiles, 'audio');
        const documentFileIds = await uploadFiles(state.documentFiles, 'document');
        const templateFileIds = await uploadFiles(state.templateFiles, 'template');

        updateProgress(40, 'Files uploaded. Starting processing...');

        // Step 2: Process
        const generateWorkflow = document.getElementById('generateWorkflowCheck').checked;
        const completeTemplates = document.getElementById('completeTemplatesCheck').checked;
        const workflowName = document.getElementById('workflowName').value || 'Generated Workflow';

        const processResponse = await fetch(`${state.apiUrl}/api/v1/process`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                audio_file_ids: audioFileIds,
                document_file_ids: documentFileIds,
                template_file_ids: templateFileIds,
                generate_workflow: generateWorkflow,
                complete_templates: completeTemplates,
                workflow_name: workflowName
            })
        });

        const processData = await processResponse.json();
        const jobId = processData.job_id;

        updateProgress(50, 'Processing in progress...');

        // Step 3: Poll for results
        const results = await pollJobStatus(jobId);

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

async function pollJobStatus(jobId) {
    while (true) {
        const response = await fetch(`${state.apiUrl}/api/v1/job/${jobId}`);
        const data = await response.json();

        if (data.status === 'completed') {
            return data;
        } else if (data.status === 'failed') {
            throw new Error(data.error || 'Processing failed');
        }

        // Wait 2 seconds before polling again
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Update progress (between 50-90%)
        const progress = 50 + Math.random() * 40;
        updateProgress(progress, 'Processing...');
    }
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

    // Display transcriptions
    if (results.transcriptions && results.transcriptions.length > 0) {
        results.transcriptions.forEach(trans => {
            resultsGrid.innerHTML += createResultCard(
                'Transcription',
                `${trans.language} - ${trans.duration_seconds.toFixed(1)}s`,
                trans.file_id,
                'transcription'
            );
        });
    }

    // Display workflows
    if (results.workflows && results.workflows.length > 0) {
        results.workflows.forEach(workflow => {
            resultsGrid.innerHTML += createResultCard(
                'Workflow Diagram',
                workflow.name,
                workflow.workflow_id,
                'workflow'
            );
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

function createResultCard(title, description, id, type) {
    return `
        <div class="result-card">
            <div class="result-info">
                <h4>${title}</h4>
                <p>${description}</p>
            </div>
            <div class="result-actions">
                <button class="btn-secondary" onclick="downloadResult('${id}', '${type}')">
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

async function downloadResult(id, type) {
    try {
        let url;
        let filename;

        if (type === 'workflow') {
            // Download both XML and diagram
            url = `${state.apiUrl}/download/workflow/${id}/xml`;
            filename = `workflow_${id}.xml`;
        } else if (type === 'document') {
            url = `${state.apiUrl}/download/document/${id}`;
            filename = `document_${id}.docx`;
        } else {
            return;
        }

        const response = await fetch(url);
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
