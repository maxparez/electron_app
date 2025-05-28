// Renderer process JavaScript

// State management
const state = {
    currentTool: 'welcome',
    selectedFiles: {
        'inv-vzd': [],
        'zor-spec': []
    },
    selectedTemplate: {
        'inv-vzd': null
    }
};

// DOM elements
const elements = {
    navItems: document.querySelectorAll('.nav-item'),
    toolContents: document.querySelectorAll('.tool-content'),
    loadingOverlay: document.getElementById('loading-overlay'),
    
    // Inv Vzd elements
    invSelectBtn: document.getElementById('select-inv-files'),
    invFilesList: document.getElementById('inv-files-list'),
    invProcessBtn: document.getElementById('process-inv-vzd'),
    invResults: document.getElementById('inv-vzd-results'),
    invTemplateBtn: document.getElementById('select-inv-template'),
    invTemplateName: document.getElementById('inv-template-name'),
    
    // Zor Spec elements
    zorSelectBtn: document.getElementById('select-zor-files'),
    zorFilesList: document.getElementById('zor-files-list'),
    zorProcessBtn: document.getElementById('process-zor-spec'),
    zorResults: document.getElementById('zor-spec-results'),
    
    // Plakat elements
    plakatForm: document.getElementById('plakat-form'),
    plakatResults: document.getElementById('plakat-results')
};

// Initialize app
function init() {
    // Setup navigation
    elements.navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tool = item.dataset.tool;
            switchTool(tool);
        });
    });
    
    // Setup file selection buttons
    elements.invSelectBtn.addEventListener('click', () => selectFiles('inv-vzd'));
    elements.zorSelectBtn.addEventListener('click', () => selectFiles('zor-spec'));
    elements.invTemplateBtn.addEventListener('click', selectInvTemplate);
    
    // Setup process buttons
    elements.invProcessBtn.addEventListener('click', processInvVzd);
    elements.zorProcessBtn.addEventListener('click', processZorSpec);
    
    // Setup plakat form
    elements.plakatForm.addEventListener('submit', generatePlakat);
    
    // Check backend connection
    checkBackendConnection();
}

// Switch between tools
function switchTool(toolId) {
    // Update navigation
    elements.navItems.forEach(item => {
        item.classList.toggle('active', item.dataset.tool === toolId);
    });
    
    // Update content
    elements.toolContents.forEach(content => {
        content.classList.remove('active');
    });
    
    const targetContent = document.getElementById(`${toolId}-tool`);
    if (targetContent) {
        targetContent.classList.add('active');
        state.currentTool = toolId;
    }
}

// Check backend connection
async function checkBackendConnection() {
    try {
        const result = await window.electronAPI.apiCall('health');
        console.log('Backend connection:', result);
    } catch (error) {
        console.error('Backend connection error:', error);
        showMessage('Chyba připojení k backend serveru', 'error');
    }
}

// File selection
async function selectFiles(tool) {
    try {
        const filePaths = await window.electronAPI.openFile({ multiple: true });
        if (filePaths.length > 0) {
            state.selectedFiles[tool] = filePaths;
            updateFilesList(tool);
            
            // Enable process button
            if (tool === 'inv-vzd') {
                checkInvVzdReady();
            } else if (tool === 'zor-spec') {
                elements.zorProcessBtn.disabled = false;
            }
        }
    } catch (error) {
        console.error('File selection error:', error);
        showMessage('Chyba při výběru souborů', 'error');
    }
}

// Update files list display
function updateFilesList(tool) {
    const filesList = tool === 'inv-vzd' ? elements.invFilesList : elements.zorFilesList;
    const files = state.selectedFiles[tool];
    
    filesList.innerHTML = '';
    
    if (files.length === 0) {
        filesList.innerHTML = '<p class="file-item">Žádné soubory nebyly vybrány</p>';
    } else {
        files.forEach(file => {
            const fileName = file.split(/[\\/]/).pop();
            const fileDiv = document.createElement('div');
            fileDiv.className = 'file-item';
            fileDiv.textContent = fileName;
            filesList.appendChild(fileDiv);
        });
    }
}

// Select template for Inv Vzd
async function selectInvTemplate() {
    try {
        const filePaths = await window.electronAPI.openFile();
        if (filePaths.length > 0) {
            state.selectedTemplate['inv-vzd'] = filePaths[0];
            const fileName = filePaths[0].split(/[\\/]/).pop();
            elements.invTemplateName.textContent = fileName;
            
            // Enable process button if both template and files are selected
            checkInvVzdReady();
        }
    } catch (error) {
        console.error('Template selection error:', error);
        showMessage('Chyba při výběru šablony', 'error');
    }
}

// Check if Inv Vzd is ready to process
function checkInvVzdReady() {
    const hasTemplate = state.selectedTemplate['inv-vzd'] !== null;
    const hasFiles = state.selectedFiles['inv-vzd'].length > 0;
    elements.invProcessBtn.disabled = !(hasTemplate && hasFiles);
}

// Process Inv Vzd
async function processInvVzd() {
    try {
        showLoading(true);
        
        // Get course type
        const courseType = document.querySelector('input[name="course-type"]:checked').value;
        
        // For now, we'll send file paths and let the backend handle file reading
        // This is because we can't use file:// protocol in renderer
        const result = await window.electronAPI.apiCall('process/inv-vzd-paths', 'POST', {
            filePaths: state.selectedFiles['inv-vzd'],
            templatePath: state.selectedTemplate['inv-vzd'],
            options: {
                courseType: courseType,
                keep_filename: true,
                optimize: false
            }
        });
        
        showLoading(false);
        
        if (result.status === 'success') {
            // Display results
            let resultHtml = `
                <h3>Zpracování dokončeno</h3>
                <p>${result.message}</p>
            `;
            
            if (result.data && result.data.files) {
                resultHtml += '<h4>Zpracované soubory:</h4><ul>';
                result.data.files.forEach(file => {
                    resultHtml += `<li>${file.source} → ${file.filename} (${file.hours} hodin)</li>`;
                });
                resultHtml += '</ul>';
            }
            
            // Show info messages
            if (result.info && result.info.length > 0) {
                resultHtml += '<h4>Informace:</h4><ul class="info-messages">';
                result.info.forEach(msg => {
                    resultHtml += `<li>${msg}</li>`;
                });
                resultHtml += '</ul>';
            }
            
            elements.invResults.innerHTML = resultHtml;
            elements.invResults.classList.add('show');
        } else {
            // Show errors
            let errorMsg = result.message || 'Zpracování selhalo';
            if (result.errors && result.errors.length > 0) {
                errorMsg += '\n\nChyby:\n' + result.errors.join('\n');
            }
            showMessage(errorMsg, 'error');
        }
        
    } catch (error) {
        showLoading(false);
        console.error('Processing error:', error);
        showMessage('Chyba při zpracování souborů: ' + error.message, 'error');
    }
}

// Process Zor Spec
async function processZorSpec() {
    try {
        showLoading(true);
        
        // Create file objects from paths
        const files = await Promise.all(
            state.selectedFiles['zor-spec'].map(async (filePath) => {
                const response = await fetch(`file://${filePath}`);
                const blob = await response.blob();
                const fileName = filePath.split(/[\\/]/).pop();
                return new File([blob], fileName);
            })
        );
        
        // Prepare form data
        const formData = new FormData();
        
        // Add files
        files.forEach(file => {
            formData.append('files', file);
        });
        
        // Add options
        const options = {};
        formData.append('options', JSON.stringify(options));
        
        // Upload and process files
        const result = await window.electronAPI.uploadFormData('process/zor-spec', formData);
        
        showLoading(false);
        
        if (result.status === 'success') {
            // Display results with detailed information
            let resultHtml = `
                <h3>Zpracování dokončeno ✅</h3>
                <div class="result-summary">
                    <p><strong>Zpracováno souborů:</strong> ${result.data.files_processed}</p>
                    <p><strong>Unikátní žáci:</strong> ${result.data.unique_students}</p>
                </div>
            `;
            
            // Show output files
            if (result.data.output_files && result.data.output_files.length > 0) {
                resultHtml += '<h4>Výstupní soubory:</h4><div class="output-files">';
                result.data.output_files.forEach(file => {
                    resultHtml += `
                        <div class="file-item">
                            <span class="file-name">${file.filename}</span>
                            <span class="file-size">(${Math.round(file.size / 1024)} KB)</span>
                            <button class="btn btn-small" onclick="downloadFile('${file.filename}', '${file.content}')">
                                💾 Stáhnout
                            </button>
                        </div>
                    `;
                });
                resultHtml += '</div>';
            }
            
            // Show info messages
            if (result.info && result.info.length > 0) {
                resultHtml += '<h4>Informace:</h4><ul class="info-messages">';
                result.info.forEach(msg => {
                    resultHtml += `<li>ℹ️ ${msg}</li>`;
                });
                resultHtml += '</ul>';
            }
            
            // Show warnings
            if (result.warnings && result.warnings.length > 0) {
                resultHtml += '<h4>Varování:</h4><ul class="warning-messages">';
                result.warnings.forEach(msg => {
                    resultHtml += `<li>⚠️ ${msg}</li>`;
                });
                resultHtml += '</ul>';
            }
            
            elements.zorResults.innerHTML = resultHtml;
            elements.zorResults.classList.add('show');
        } else {
            // Show errors
            let errorMsg = result.message || 'Zpracování selhalo';
            if (result.errors && result.errors.length > 0) {
                errorMsg += '\n\nChyby:\n' + result.errors.join('\n');
            }
            showMessage(errorMsg, 'error');
        }
        
    } catch (error) {
        showLoading(false);
        console.error('Processing error:', error);
        showMessage('Chyba při zpracování souborů: ' + error.message, 'error');
    }
}

// Generate Plakat
async function generatePlakat(event) {
    event.preventDefault();
    
    try {
        // Get form data
        const projectsInput = document.getElementById('projects-input').value;
        const orientation = document.querySelector('input[name="orientation"]:checked').value;
        const commonText = document.getElementById('common-text').value;
        
        // Parse projects input
        const projects = parseProjectsInput(projectsInput);
        if (projects.length === 0) {
            showMessage('Nebyli nalezeny žádné platné projekty', 'error');
            return;
        }
        
        // Show loading with progress
        showLoading(true, {
            text: `Generuji plakáty...`,
            showProgress: true,
            total: projects.length
        });
        
        // Send to backend
        const requestData = {
            projects: projects,
            orientation: orientation,
            common_text: commonText
        };
        
        const result = await window.electronAPI.apiCall('process/plakat', 'POST', requestData);
        
        showLoading(false);
        
        if (result.status === 'success') {
            // Display results
            let resultHtml = `
                <h3>Plakáty vygenerovány ✅</h3>
                <div class="result-summary">
                    <p><strong>Úspěšně:</strong> ${result.data.successful_projects}/${result.data.total_projects}</p>
                    ${result.data.failed_projects > 0 ? `<p><strong>Selhalo:</strong> ${result.data.failed_projects}</p>` : ''}
                </div>
            `;
            
            // Show output files
            if (result.data.output_files && result.data.output_files.length > 0) {
                resultHtml += '<h4>Vygenerované plakáty:</h4><div class="output-files">';
                result.data.output_files.forEach(file => {
                    resultHtml += `
                        <div class="file-item">
                            <span class="file-name">${file.filename}</span>
                            <span class="file-size">(${Math.round(file.size / 1024)} KB)</span>
                            <button class="btn btn-small" onclick="downloadFile('${file.filename}', '${file.content}')">
                                💾 Stáhnout
                            </button>
                        </div>
                    `;
                });
                resultHtml += '</div>';
            }
            
            elements.plakatResults.innerHTML = resultHtml;
            elements.plakatResults.classList.add('show');
        } else {
            showMessage(result.message || 'Generování selhalo', 'error');
        }
        
    } catch (error) {
        showLoading(false);
        console.error('Generation error:', error);
        showMessage('Chyba při generování plakátu: ' + error.message, 'error');
    }
}

// Save plakat
async function savePlakat(filePath) {
    try {
        const savePath = await window.electronAPI.saveFile('plakat.pdf');
        if (savePath) {
            // TODO: Copy file from temp to save location
            showMessage('Plakát byl uložen', 'success');
        }
    } catch (error) {
        console.error('Save error:', error);
        showMessage('Chyba při ukládání plakátu', 'error');
    }
}

// Parse projects input
function parseProjectsInput(input) {
    const projects = [];
    const lines = input.trim().split('\n');
    
    for (const line of lines) {
        const trimmedLine = line.trim();
        if (!trimmedLine) continue;
        
        let parts;
        // Try different separators
        if (trimmedLine.includes(' - ')) {
            parts = trimmedLine.split(' - ', 2);
        } else if (trimmedLine.includes(',')) {
            parts = trimmedLine.split(',', 2);
        } else if (trimmedLine.includes('\t')) {
            parts = trimmedLine.split('\t', 2);
        } else {
            continue; // Skip invalid lines
        }
        
        if (parts.length === 2) {
            const id = parts[0].trim();
            const name = parts[1].trim();
            
            if (id && name) {
                projects.push({ id, name });
            }
        }
    }
    
    return projects;
}

// Show/hide loading overlay with optional progress
function showLoading(show, options = {}) {
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    const progressContainer = document.getElementById('progress-container');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    if (show) {
        loadingOverlay.classList.add('show');
        loadingText.textContent = options.text || 'Zpracovávám...';
        
        if (options.showProgress) {
            progressContainer.style.display = 'block';
            updateProgress(0, options.total || 0);
        } else {
            progressContainer.style.display = 'none';
        }
    } else {
        loadingOverlay.classList.remove('show');
        progressContainer.style.display = 'none';
        progressFill.style.width = '0%';
    }
}

// Update progress bar
function updateProgress(current, total) {
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    const percentage = total > 0 ? (current / total) * 100 : 0;
    progressFill.style.width = percentage + '%';
    progressText.textContent = `${current} / ${total}`;
}

// Show message
function showMessage(text, type = 'info') {
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.textContent = text;
    
    const content = document.querySelector('.content');
    content.insertBefore(message, content.firstChild);
    
    // Remove after 5 seconds
    setTimeout(() => {
        message.remove();
    }, 5000);
}

// Download file with save dialog
async function downloadFile(filename, content) {
    try {
        // Get save path from user
        const savePath = await window.electronAPI.saveFile(filename);
        
        if (savePath) {
            // Decode hex content to binary
            const binaryData = hexToBytes(content);
            
            // Write file using Node.js fs module through Electron API
            await window.electronAPI.writeFile(savePath, binaryData);
            
            showMessage(window.i18n ? window.i18n.t('invVzd.results.saved', {filename}) : `Soubor ${filename} byl úspěšně uložen`, 'success');
        }
    } catch (error) {
        console.error('Download error:', error);
        showMessage('Chyba při ukládání souboru: ' + error.message, 'error');
    }
}

// Convert hex string to byte array
function hexToBytes(hex) {
    const bytes = new Uint8Array(hex.length / 2);
    for (let i = 0; i < hex.length; i += 2) {
        bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
    }
    return bytes;
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    // Load translations first
    if (window.i18n) {
        await window.i18n.load('cs');
        window.i18n.translatePage();
    }
    
    // Then initialize the app
    init();
});