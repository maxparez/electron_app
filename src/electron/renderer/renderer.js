// Renderer process JavaScript

// State management
const state = {
    currentTool: 'welcome',
    selectedFiles: {
        'inv-vzd': [],
        'zor-spec': []
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
        const filePaths = await window.electronAPI.openFile();
        if (filePaths.length > 0) {
            state.selectedFiles[tool] = filePaths;
            updateFilesList(tool);
            
            // Enable process button
            if (tool === 'inv-vzd') {
                elements.invProcessBtn.disabled = false;
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

// Process Inv Vzd
async function processInvVzd() {
    try {
        showLoading(true);
        
        // Get course type
        const courseType = document.querySelector('input[name="course-type"]:checked').value;
        
        // Create file objects from paths
        const files = await Promise.all(
            state.selectedFiles['inv-vzd'].map(async (filePath) => {
                const response = await fetch(`file://${filePath}`);
                const blob = await response.blob();
                const fileName = filePath.split(/[\\/]/).pop();
                return new File([blob], fileName);
            })
        );
        
        // Upload and process files
        const result = await window.electronAPI.uploadFiles('process/inv-vzd', files, {
            courseType: courseType
        });
        
        showLoading(false);
        
        // Display results
        elements.invResults.innerHTML = `
            <h3>Zpracování dokončeno</h3>
            <p>${result.message}</p>
            <p>Zpracováno souborů: ${result.data.processed}</p>
        `;
        elements.invResults.classList.add('show');
        
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
        
        // Upload and process files
        const result = await window.electronAPI.uploadFiles('process/zor-spec', files);
        
        showLoading(false);
        
        // Display results
        elements.zorResults.innerHTML = `
            <h3>Zpracování dokončeno</h3>
            <p>${result.message}</p>
            <p>Zpracováno souborů: ${result.data.processed}</p>
        `;
        elements.zorResults.classList.add('show');
        
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
        showLoading(true);
        
        // Get form data
        const formData = {
            projectName: document.getElementById('project-name').value,
            projectDescription: document.getElementById('project-description').value,
            projectDate: document.getElementById('project-date').value,
            projectLocation: document.getElementById('project-location').value
        };
        
        // Send to backend
        const result = await window.electronAPI.apiCall('generate/plakat', 'POST', formData);
        
        showLoading(false);
        
        // Display results
        elements.plakatResults.innerHTML = `
            <h3>Plakát vygenerován</h3>
            <p>${result.message}</p>
            <p>Soubor: ${result.data.file_path}</p>
            <button class="btn btn-primary" onclick="savePlakat('${result.data.file_path}')">
                Uložit plakát
            </button>
        `;
        elements.plakatResults.classList.add('show');
        
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

// Show/hide loading overlay
function showLoading(show) {
    elements.loadingOverlay.classList.toggle('show', show);
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

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);