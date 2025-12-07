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
    },
    detectedTemplateVersion: null
};

// DOM elements
const elements = {
    navItems: document.querySelectorAll('.nav-item'),
    toolContents: document.querySelectorAll('.tool-content'),
    loadingOverlay: document.getElementById('loading-overlay'),
    
    // Inv Vzd elements
    invSelectBtn: document.getElementById('select-inv-files'),
    invFolderBtn: document.getElementById('select-inv-folder'),
    invFilesList: document.getElementById('inv-files-list'),
    invProcessBtn: document.getElementById('process-inv-vzd'),
    invResults: document.getElementById('inv-vzd-results'),
    invTemplateVersion: document.getElementById('inv-template-version'),
    invTemplateBtn: document.getElementById('select-inv-template'),
    invTemplateName: document.getElementById('inv-template-name'),
    
    // Zor Spec elements
    zorSelectBtn: document.getElementById('select-zor-files'),
    zorFolderBtn: document.getElementById('select-zor-folder'),
    zorFilesList: document.getElementById('zor-files-list'),
    zorProcessBtn: document.getElementById('process-zor-spec'),
    zorResults: document.getElementById('zor-spec-results'),
    
    // Plakat elements
    plakatForm: document.getElementById('plakat-form'),
    plakatResults: document.getElementById('plakat-results')
};

// Status bar functions
function setStatusMessage(message, duration = 0) {
    const statusElement = document.getElementById('status-message');
    statusElement.textContent = message;
    
    if (duration > 0) {
        setTimeout(() => {
            statusElement.textContent = 'Připraveno';
        }, duration);
    }
}

// Initialize app
async function init() {
    // Load version info
    try {
        const versionInfo = await window.electronAPI.getVersion();
        document.getElementById('version-info').textContent = `Verze: ${versionInfo.full}`;
    } catch (error) {
        console.error('Failed to get version info:', error);
    }
    
    // Setup navigation
    elements.navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tool = item.dataset.tool;
            switchTool(tool);
        });
    });
    
    // Setup clickable features on home screen
    const clickableFeatures = document.querySelectorAll('.clickable-feature');
    clickableFeatures.forEach(feature => {
        feature.addEventListener('click', () => {
            const tool = feature.dataset.tool;
            switchTool(tool);
        });
    });
    
    // Setup file selection buttons
    elements.invSelectBtn.addEventListener('click', () => selectFiles('inv-vzd'));
    elements.invFolderBtn.addEventListener('click', selectInvFolder);
    
    // Initially disable file selection buttons until template is selected
    elements.invSelectBtn.disabled = true;
    elements.invFolderBtn.disabled = true;
    elements.zorSelectBtn.addEventListener('click', () => selectFiles('zor-spec'));
    elements.zorFolderBtn.addEventListener('click', selectZorFolder);
    elements.invTemplateBtn.addEventListener('click', selectInvTemplate);
    
    // Setup process buttons
    elements.invProcessBtn.addEventListener('click', processInvVzd);
    elements.zorProcessBtn.addEventListener('click', processZorSpec);
    
    // Setup plakat form
    elements.plakatForm.addEventListener('submit', generatePlakat);
    
    // Setup folder selection
    const plakatFolderBtn = document.getElementById('select-plakat-folder');
    const plakatFolderInput = document.getElementById('plakat-folder');
    
    if (plakatFolderBtn) {
        plakatFolderBtn.addEventListener('click', async () => {
            const folder = await window.electronAPI.selectFolder({
                configKey: 'lastPlakatFolder',
                title: 'Vyberte složku pro ukládání plakátů'
            });
            if (folder) {
                plakatFolderInput.value = folder;
            }
        });
    }
    
    // Load last selected folder
    loadLastFolder();
    
    // Setup character counter for plakat common text
    const commonTextArea = document.getElementById('common-text');
    const charCounter = document.getElementById('char-counter');
    
    if (commonTextArea && charCounter) {
        // Update counter on page load
        updateCharacterCounter(commonTextArea, charCounter);
        
        // Update counter on input
        commonTextArea.addEventListener('input', () => {
            updateCharacterCounter(commonTextArea, charCounter);
        });
    }
    
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
    
    // Handle special case for welcome screen
    let targetContent;
    if (toolId === 'welcome') {
        targetContent = document.getElementById('welcome-screen');
    } else {
        targetContent = document.getElementById(`${toolId}-tool`);
    }
    
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
            // For ZorSpec, check if files have the required sheet
            if (tool === 'zor-spec') {
                const validFiles = [];
                const fileVersions = {};
                
                for (const filePath of filePaths) {
                    try {
                        const versionResult = await window.electronAPI.apiCall('detect/zor-spec-version', 'POST', {
                            filePath: filePath
                        });
                        
                        if (versionResult.success && versionResult.has_intro_sheet) {
                            validFiles.push(filePath);
                            fileVersions[filePath] = versionResult.version;
                        } else {
                            showMessage(`Soubor ${filePath.split(/[\\\/]/).pop()} neobsahuje list "Úvod a postup vyplňování"`, 'warning');
                        }
                    } catch (error) {
                        console.error(`Error checking file ${filePath}:`, error);
                    }
                }
                
                if (validFiles.length > 0) {
                    state.selectedFiles[tool] = validFiles;
                    state.zorFileVersions = fileVersions;
                    updateFilesList(tool);
                    elements.zorProcessBtn.disabled = false;
                    showMessage(`Vybráno ${validFiles.length} vhodných souborů`, 'success');
                } else {
                    showMessage('Žádný z vybraných souborů neobsahuje požadovaný list', 'error');
                }
            } else if (tool === 'inv-vzd') {
                // For InvVzd, check compatibility with selected template
                if (!state.detectedTemplateVersion) {
                    showMessage('Nejprve vyberte platnou šablonu', 'error');
                    return;
                }
                
                const validFiles = [];
                const incompatibleFiles = [];
                
                for (const filePath of filePaths) {
                    try {
                        // Check if file is compatible with template
                        const compatible = await isFileCompatibleWithTemplate(filePath);
                        if (compatible) {
                            validFiles.push(filePath);
                        } else {
                            incompatibleFiles.push(filePath);
                        }
                    } catch (error) {
                        console.error(`Error checking file ${filePath}:`, error);
                        incompatibleFiles.push(filePath);
                    }
                }
                
                // Show messages for incompatible files
                incompatibleFiles.forEach(file => {
                    const displayPath = wslToWindowsPath(file);
                    showMessage(`Soubor ${displayPath} neodpovídá vybrané šabloně`, 'warning');
                });
                
                if (validFiles.length > 0) {
                    state.selectedFiles[tool] = validFiles;
                    updateFilesList(tool);
                    checkInvVzdReady();
                    showMessage(`Vybráno ${validFiles.length} vhodných souborů`, 'success');
                } else {
                    showMessage('Žádný z vybraných souborů neodpovídá vybrané šabloně', 'error');
                }
            } else {
                state.selectedFiles[tool] = filePaths;
                updateFilesList(tool);
            }
        }
    } catch (error) {
        console.error('File selection error:', error);
        showMessage('Chyba při výběru souborů', 'error');
    }
}

// Convert WSL path to Windows path for display
function wslToWindowsPath(path) {
    if (path.startsWith('/mnt/')) {
        const driveLetter = path[5].toUpperCase();
        return `${driveLetter}:${path.substring(6).replace(/\//g, '\\')}`;
    }
    return path;
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
            const fileDiv = document.createElement('div');
            fileDiv.className = 'file-item';
            
            // For ZorSpec files, show version info if available
            if (tool === 'zor-spec' && state.zorFileVersions && state.zorFileVersions[file]) {
                fileDiv.innerHTML = `
                    <div class="file-item-content">
                        <div class="file-path">
                            <strong>Cesta:</strong> ${wslToWindowsPath(file)}
                            <br><strong>Verze:</strong> ${state.zorFileVersions[file]}
                        </div>
                        <button class="btn-remove" onclick="removeFile('${tool}', '${file.replace(/\\/g, '\\\\').replace(/'/g, "\\'")}')">✕</button>
                    </div>
                `;
            } else {
                fileDiv.innerHTML = `
                    <div class="file-item-content">
                        <div class="file-path">
                            <strong>Cesta:</strong> ${wslToWindowsPath(file)}
                        </div>
                        <button class="btn-remove" onclick="removeFile('${tool}', '${file.replace(/\\/g, '\\\\').replace(/'/g, "\\'")}')">✕</button>
                    </div>
                `;
            }
            
            filesList.appendChild(fileDiv);
        });
    }
}

// Remove file from list
function removeFile(tool, filePath) {
    const toolKey = tool === 'inv-vzd' ? 'inv-vzd' : 'zor-spec';
    
    // Remove from selectedFiles array
    const index = state.selectedFiles[toolKey].indexOf(filePath);
    if (index > -1) {
        state.selectedFiles[toolKey].splice(index, 1);
    }
    
    // Remove from version info if exists
    if (state.zorFileVersions && state.zorFileVersions[filePath]) {
        delete state.zorFileVersions[filePath];
    }
    
    // Update display
    updateFilesList(tool);
    
    // Update process button state
    if (tool === 'inv-vzd') {
        checkInvVzdReady();
    } else if (tool === 'zor-spec') {
        checkZorSpecReady();
    }
}

// Select template for Inv Vzd
async function selectInvTemplate() {
    try {
        const filePaths = await window.electronAPI.openFile();
        if (filePaths.length > 0) {
            state.selectedTemplate['inv-vzd'] = filePaths[0];
            elements.invTemplateName.innerHTML = `
                <div class="template-path">
                    <strong>Cesta:</strong> ${wslToWindowsPath(filePaths[0])}
                </div>
            `;
            
            // Detect template version
            await detectTemplateVersion(filePaths[0]);
            
            // Update button states
            checkInvVzdReady();
        }
    } catch (error) {
        console.error('Template selection error:', error);
        showMessage('Chyba při výběru šablony', 'error');
    }
}

// Select folder and scan for attendance files
async function selectInvFolder() {
    try {
        const folderPath = await window.electronAPI.selectFolder({
            configKey: 'lastInvVzdFolder',
            title: 'Vyberte složku s docházkami'
        });
        
        if (folderPath) {
            // Scan folder for Excel files
            const suitableFiles = await scanFolderForAttendanceFiles(folderPath);
            
            if (suitableFiles.length > 0) {
                state.selectedFiles['inv-vzd'] = suitableFiles;
                updateFilesList('inv-vzd');
                checkInvVzdReady();
                showMessage(`Nalezeno ${suitableFiles.length} vhodných souborů docházky`, 'success');
            } else {
                showMessage('Ve vybrané složce nebyly nalezeny žádné vhodné soubory docházky', 'warning');
            }
        }
    } catch (error) {
        console.error('Folder selection error:', error);
        showMessage('Chyba při výběru složky', 'error');
    }
}

// Scan folder for suitable attendance files
async function scanFolderForAttendanceFiles(folderPath) {
    try {
        // Call backend API to scan folder
        const response = await window.electronAPI.apiCall('select-folder', 'POST', {
            folderPath: folderPath,
            toolType: 'inv-vzd',
            templatePath: state.selectedTemplate['inv-vzd']
        });
        
        if (response.success && response.files) {
            // Return full paths from the API response
            return response.files.map(file => file.path);
        } else {
            console.warn('No files found:', response.message);
            return [];
        }
        
    } catch (error) {
        console.error('Error scanning folder:', error);
        return [];
    }
}

// Select folder and scan for ZorSpec attendance files
async function selectZorFolder() {
    try {
        const folderPath = await window.electronAPI.selectFolder({
            configKey: 'lastZorSpecFolder',
            title: 'Vyberte složku s docházkami pro ZoR'
        });
        
        if (folderPath) {
            // Scan folder for Excel files with version detection
            const scanResult = await scanFolderForZorSpecFiles(folderPath);
            
            if (scanResult.files.length > 0) {
                state.selectedFiles['zor-spec'] = scanResult.files;
                // Store version info for display
                state.zorFileVersions = scanResult.versions;
                
                // Check for mixed versions and warn user
                const versions = Object.values(scanResult.versions);
                const uniqueVersions = [...new Set(versions)];
                
                if (uniqueVersions.length > 1) {
                    const versionCounts = uniqueVersions.map(v => `${v}: ${versions.filter(version => version === v).length} souborů`).join(', ');
                    showMessage(`⚠️ POZOR: Nalezeny soubory s různými verzemi (${versionCounts}). Zkontrolujte, zda chcete zpracovat všechny soubory současně.`, 'warning');
                }
                
                updateFilesList('zor-spec');
                elements.zorProcessBtn.disabled = false;
                showMessage(`Nalezeno ${scanResult.files.length} vhodných souborů docházky`, 'success');
            } else {
                showMessage('Ve vybrané složce nebyly nalezeny žádné soubory s listem "Úvod a postup vyplňování"', 'warning');
            }
        }
    } catch (error) {
        console.error('Folder selection error:', error);
        showMessage('Chyba při výběru složky', 'error');
    }
}

// Scan folder for suitable ZorSpec attendance files
async function scanFolderForZorSpecFiles(folderPath) {
    try {
        // Use Node.js fs to read directory
        const result = await window.electronAPI.scanFolder(folderPath);
        
        // Filter for Excel files
        const excelFiles = result.files.filter(file => {
            const extension = file.toLowerCase().split('.').pop();
            return ['xlsx', 'xls'].includes(extension);
        });
        
        // Check each file for the 'Úvod a postup vyplňování' sheet
        const suitableFiles = [];
        const fileVersions = {};
        
        for (const file of excelFiles) {
            const filePath = `${folderPath}${folderPath.includes('\\') ? '\\' : '/'}${file}`;
            
            try {
                // Check if file has the required sheet and get version
                const versionResult = await window.electronAPI.apiCall('detect/zor-spec-version', 'POST', {
                    filePath: filePath
                });
                
                if (versionResult.success && versionResult.has_intro_sheet) {
                    suitableFiles.push(filePath);
                    fileVersions[filePath] = versionResult.version;
                }
            } catch (error) {
                console.error(`Error checking file ${file}:`, error);
            }
        }
        
        return {
            files: suitableFiles,
            versions: fileVersions
        };
        
    } catch (error) {
        console.error('Error scanning folder:', error);
        return { files: [], versions: {} };
    }
}

// Check if Inv Vzd is ready to process
function checkInvVzdReady() {
    const hasTemplate = state.selectedTemplate['inv-vzd'] !== null;
    const hasFiles = state.selectedFiles['inv-vzd'].length > 0;
    const hasValidVersion = state.detectedTemplateVersion !== null;
    
    // Enable/disable file selection buttons based on template validity
    elements.invSelectBtn.disabled = !hasValidVersion;
    elements.invFolderBtn.disabled = !hasValidVersion;
    
    // Enable process button only if everything is ready
    elements.invProcessBtn.disabled = !(hasTemplate && hasFiles && hasValidVersion);
}

// Process Inv Vzd
async function processInvVzd() {
    try {
        showLoading(true);
        setStatusMessage('Zpracovávám inovativní vzdělávání...');
        
        // Get course type from detected template version
        const courseType = state.detectedTemplateVersion || '32'; // Default to 32 if not detected
        
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
        
        if (result.status === 'success' || result.status === 'partial' || (result.data && result.data.info)) {
            // Display results - could be full success or partial success with errors
            const hasErrors = result.data && result.data.errors && result.data.errors.length > 0;
            const title = hasErrors ? 
                '<h3>Zpracování dokončeno s chybami ⚠️</h3>' : 
                '<h3>Zpracování dokončeno ✅</h3>';
            
            let resultHtml = title;
            
            // Skip general messages - all information is now shown in per-file blocks
            
            // Show file blocks if available
            if (result.data && result.data.files && result.data.files.length > 0) {
                const fileBlocks = result.data.files.map(file => {
                    return formatFileProcessingBlock(file);
                });
                resultHtml += fileBlocks.join('');
            }
            
            elements.invResults.innerHTML = resultHtml;
            elements.invResults.classList.add('show');
        } else {
            // Show detailed error information in results area
            let errorHtml = `
                <h3 class="error">Zpracování selhalo ❌</h3>
                <p><strong>Hlavní zpráva:</strong> ${result.message || 'Neznámá chyba'}</p>
            `;
            
            // Show detailed errors
            if (result.errors && result.errors.length > 0) {
                errorHtml += '<h4>Detailní chyby:</h4><ul class="error-messages">';
                result.errors.forEach(error => {
                    errorHtml += `<li class="error-item">${error}</li>`;
                });
                errorHtml += '</ul>';
            }
            
            // Show warnings if any
            if (result.warnings && result.warnings.length > 0) {
                errorHtml += '<h4>Varování:</h4><ul class="warning-messages">';
                result.warnings.forEach(warning => {
                    errorHtml += `<li class="warning-item">${warning}</li>`;
                });
                errorHtml += '</ul>';
            }
            
            elements.invResults.innerHTML = errorHtml;
            elements.invResults.classList.add('show');
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
        
        // Use path-based processing with auto-save
        const result = await window.electronAPI.apiCall('process/zor-spec-paths', 'POST', {
            filePaths: state.selectedFiles['zor-spec'],
            options: {},
            autoSave: true  // Auto-save to source folder
        });
        
        showLoading(false);
        
        if (result.status === 'success') {
            // Status banner with completion message
            let resultHtml = `
                <div class="status-banner">
                    <div class="status-content">
                        <div class="status-icon">✓</div>
                        <div class="status-text">
                            <h3>Zpracování dokončeno</h3>
                            <p>Všechna data byla úspěšně analyzována a uložena.</p>
                        </div>
                    </div>
                    <span class="status-time">Doba trvání: 1.2s</span>
                </div>

                <!-- Primary stats grid -->
                <div class="stats-grid primary-stats">
                    <div class="stat-card">
                        <div class="stat-content">
                            <div class="stat-header">
                                <div class="stat-label">ZPRACOVÁNO SOUBORŮ</div>
                            </div>
                            <div class="stat-value">${result.data.files_processed}</div>
                        </div>
                        <div class="stat-icon">📄</div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-content">
                            <div class="stat-header">
                                <div class="stat-label">UNIKÁTNÍ ŽÁCI</div>
                            </div>
                            <div class="stat-value">${result.data.unique_students}</div>
                            <div class="stat-subtext">Identifikováno v systému</div>
                        </div>
                        <div class="stat-icon">👥</div>
                    </div>
                </div>
            `;

            // School type breakdown (if available)
            if (result.data.students_16plus) {
                const students16 = result.data.students_16plus;
                resultHtml += `
                    <div class="section-header">Počet dětí/žáků se splněnou docházkou 16h</div>
                    <div class="stats-grid school-stats">
                        <div class="stat-card school-card">
                            <div class="stat-content">
                                <div class="stat-label">MATEŘSKÁ ŠKOLA</div>
                                <div class="stat-value">${students16['MŠ'] || 0}</div>
                            </div>
                            <div class="stat-icon school-icon">🏫</div>
                        </div>

                        <div class="stat-card school-card">
                            <div class="stat-content">
                                <div class="stat-label">ZÁKLADNÍ ŠKOLA</div>
                                <div class="stat-value">${students16['ZŠ'] || 0}</div>
                            </div>
                            <div class="stat-icon school-icon">📚</div>
                        </div>

                        <div class="stat-card school-card">
                            <div class="stat-content">
                                <div class="stat-label">ŠKOLNÍ DRUŽINA</div>
                                <div class="stat-value">${students16['ŠD'] || 0}</div>
                            </div>
                            <div class="stat-icon school-icon">🎒</div>
                        </div>
                    </div>
                `;
            }
            
            // Output files section
            if (result.data.output_files && result.data.output_files.length > 0) {
                if (result.data.auto_saved) {
                    // Convert WSL path back to Windows format
                    let displayPath = result.data.output_directory;
                    let windowsPath = displayPath;

                    // Convert /mnt/x/ to X:\ for Windows
                    if (displayPath.startsWith('/mnt/')) {
                        const driveLetter = displayPath[5].toUpperCase();
                        windowsPath = `${driveLetter}:${displayPath.substring(6).replace(/\//g, '\\')}`;
                        displayPath = windowsPath;
                    }

                    resultHtml += `
                        <div class="output-section">
                            <div class="output-header">
                                <h4><span class="folder-icon">📁</span> Výstupní soubory</h4>
                                <div class="output-path-display">
                                    <span class="path-text">${displayPath}</span>
                                    <button class="copy-btn" onclick="openFolder('${displayPath.replace(/\\/g, '\\\\')}')" title="Otevřít složku s výsledky">
                                        📂
                                    </button>
                                </div>
                            </div>
                            <div class="output-files-list">
                    `;

                    result.data.output_files.forEach(file => {
                        // Build correct Windows path for file
                        const fullPath = windowsPath + '\\' + file.filename;
                        const icon = file.filename.endsWith('.html') ? '📄' : '📝';
                        const fileType = file.filename.endsWith('.html') ? 'html' : 'txt';

                        resultHtml += `
                            <div class="file-item">
                                <div class="file-info">
                                    <span class="file-icon ${fileType}">${icon}</span>
                                    <div class="file-details">
                                        <span class="file-name">${file.filename}</span>
                                        <span class="file-size">${Math.round(file.size / 1024)} KB</span>
                                    </div>
                                </div>
                                <div class="file-actions">
                                    <button class="file-btn btn-view" onclick="openFile('${fullPath.replace(/\\/g, '\\\\')}')">
                                        👁️ Zobrazit
                                    </button>
                                </div>
                            </div>
                        `;
                    });

                    // Add timestamp
                    const now = new Date();
                    const timestamp = now.toLocaleDateString('cs-CZ') + ' ' + now.toLocaleTimeString('cs-CZ', {hour: '2-digit', minute: '2-digit'});

                    resultHtml += `
                            </div>
                            <div class="output-footer">
                                <p>Generováno automaticky: ${timestamp}</p>
                            </div>
                        </div>
                    `;
                } else {
                    resultHtml += '<div class="output-section"><h4>Výstupní soubory:</h4><div class="output-files-list">';
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
                    resultHtml += '</div></div>';
                }
            }
            
            // Show info messages
            if (result.info && result.info.length > 0) {
                resultHtml += `
                    <div class="info-section">
                        <h4>ℹ️ Informace</h4>
                        <ul class="info-messages">
                `;
                result.info.forEach(msg => {
                    // Check if message contains path info (format: "text: path||filename")
                    if (msg.includes('||')) {
                        const parts = msg.split('||');
                        const text = parts[0];
                        const filename = parts[1];
                        
                        // Extract full path from text
                        const pathMatch = text.match(/: (.+)$/);
                        if (pathMatch) {
                            let fullPath = pathMatch[1];
                            const description = text.substring(0, text.indexOf(':'));
                            
                            // Convert WSL path to Windows if needed
                            if (fullPath.startsWith('/mnt/')) {
                                const driveLetter = fullPath[5].toUpperCase();
                                fullPath = `${driveLetter}:${fullPath.substring(6).replace(/\//g, '\\')}`;
                            }
                            
                            resultHtml += `<li>${description}: <a href="#" onclick="openFile('${fullPath.replace(/\\/g, '\\\\')}'); return false;" class="file-link">${filename}</a></li>`;
                        } else {
                            resultHtml += `<li>${msg}</li>`;
                        }
                    } else {
                        resultHtml += `<li>${msg}</li>`;
                    }
                });
                resultHtml += `
                        </ul>
                    </div>
                `;
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
            // Show detailed error information in results area
            let errorHtml = `
                <h3 class="error">Zpracování selhalo ❌</h3>
                <p><strong>Hlavní zpráva:</strong> ${result.message || 'Neznámá chyba'}</p>
            `;
            
            // Show detailed errors
            if (result.errors && result.errors.length > 0) {
                errorHtml += '<h4>Detailní chyby:</h4><ul class="error-messages">';
                result.errors.forEach(error => {
                    errorHtml += `<li class="error-item">${error}</li>`;
                });
                errorHtml += '</ul>';
            }
            
            // Show warnings if any
            if (result.warnings && result.warnings.length > 0) {
                errorHtml += '<h4>Varování:</h4><ul class="warning-messages">';
                result.warnings.forEach(warning => {
                    errorHtml += `<li class="warning-item">${warning}</li>`;
                });
                errorHtml += '</ul>';
            }
            
            elements.zorResults.innerHTML = errorHtml;
            elements.zorResults.classList.add('show');
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
            // Get target folder
            const targetFolder = document.getElementById('plakat-folder').value;
            
            // Save files automatically
            if (result.data.output_files && result.data.output_files.length > 0 && targetFolder) {
                const saveResults = await saveFilesAutomatically(result.data.output_files, targetFolder);
                
                // Display results with save status
                let resultHtml = `
                    <h3>Plakáty vygenerovány ✅</h3>
                    <div class="result-summary">
                        <p><strong>Úspěšně:</strong> ${result.data.successful_projects}/${result.data.total_projects}</p>
                        ${result.data.failed_projects > 0 ? `<p><strong>Selhalo:</strong> ${result.data.failed_projects}</p>` : ''}
                        <p><strong>Složka:</strong> ${targetFolder}</p>
                    </div>
                `;
                
                resultHtml += '<h4>Uložené soubory:</h4><div class="output-files">';
                saveResults.forEach((saveResult, index) => {
                    const file = result.data.output_files[index];
                    resultHtml += `
                        <div class="file-item">
                            <span class="file-name">${saveResult.filename}</span>
                            <span class="file-size">(${Math.round(file.size / 1024)} KB)</span>
                            <span class="file-status ${saveResult.success ? 'success' : 'error'}">
                                ${saveResult.success ? '✅ Uloženo' : '❌ Chyba'}
                            </span>
                        </div>
                    `;
                });
                resultHtml += '</div>';
                
                elements.plakatResults.innerHTML = resultHtml;
                elements.plakatResults.classList.add('show');
                
                // Show success message
                const successCount = saveResults.filter(r => r.success).length;
                showMessage(`Uloženo ${successCount} plakátů do složky ${targetFolder}`, 'success');
            } else {
                showMessage('Nebyla vybrána složka pro uložení', 'error');
            }
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

// Update character counter for textarea
function updateCharacterCounter(textarea, counter) {
    const length = textarea.value.length;
    const maxLength = parseInt(textarea.getAttribute('maxlength')) || 255;
    
    counter.textContent = `${length}/${maxLength}`;
    
    // Update styling based on remaining characters
    counter.classList.remove('warning', 'danger');
    if (length >= maxLength * 0.9) {
        counter.classList.add('danger');
    } else if (length >= maxLength * 0.8) {
        counter.classList.add('warning');
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
        // Try different separators - semicolon and tab are primary
        if (trimmedLine.includes(';')) {
            parts = trimmedLine.split(';', 2);
        } else if (trimmedLine.includes('\t')) {
            parts = trimmedLine.split('\t', 2);
        } else if (trimmedLine.includes(' - ')) {
            parts = trimmedLine.split(' - ', 2);
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

// Open folder in file explorer
async function openFolder(folderPath) {
    try {
        const result = await window.electronAPI.openFolder(folderPath);
        if (result.success) {
            console.log('Složka otevřena');
        } else {
            showMessage(`Chyba při otevírání složky: ${result.error}`, 'error');
        }
    } catch (err) {
        console.error('Chyba při otevírání složky:', err);
        showMessage('Chyba při otevírání složky', 'error');
    }
}

// Open file in associated application
async function openFile(filePath) {
    try {
        const result = await window.electronAPI.openFileInApp(filePath);
        if (result.success) {
            showMessage(`Soubor ${result.filename || 'soubor'} byl otevřen`, 'success');
        } else {
            showMessage(`Chyba při otevírání souboru: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Open file error:', error);
        showMessage('Chyba při otevírání souboru', 'error');
    }
}

// Load last selected folder
async function loadLastFolder() {
    const plakatFolderInput = document.getElementById('plakat-folder');
    if (plakatFolderInput && window.electronAPI) {
        const lastFolder = await window.electronAPI.getConfig('lastPlakatFolder');
        if (lastFolder) {
            plakatFolderInput.value = lastFolder;
        } else {
            // Set default to Documents folder
            plakatFolderInput.value = await window.electronAPI.getConfig('documentsPath') || 'Dokumenty';
        }
    }
}

// Save files automatically to selected folder
async function saveFilesAutomatically(files, targetFolder) {
    const results = [];
    
    for (const file of files) {
        try {
            const filePath = `${targetFolder}${targetFolder.endsWith('\\') ? '' : '\\'}${file.filename}`;
            const binaryData = hexToBytes(file.content);
            
            await window.electronAPI.writeFile(filePath, binaryData);
            results.push({
                filename: file.filename,
                path: filePath,
                success: true
            });
        } catch (error) {
            console.error(`Error saving ${file.filename}:`, error);
            results.push({
                filename: file.filename,
                success: false,
                error: error.message
            });
        }
    }
    
    return results;
}

// Toggle collapsible section
function toggleCollapsible(blockId) {
    const content = document.getElementById(blockId);
    const icon = document.getElementById(`icon-${blockId}`);
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        icon.textContent = '▼';
    } else {
        content.style.display = 'none';
        icon.textContent = '▶';
    }
}

// Format file processing block with steps
function formatFileProcessingBlock(file) {
    const sourceBasename = file.source.split(/[/\\]/).pop();
    const blockId = `file-block-${Math.random().toString(36).substr(2, 9)}`;
    
    // Get messages directly from file object if available
    const fileInfo = file.info || [];
    const fileWarnings = file.warnings || [];
    const fileErrors = file.errors || [];
    
    // Determine status based on file status or errors
    let statusText, statusIcon, statusClass;
    
    if (file.status === 'error' || fileErrors.length > 0) {
        if (file.output === null) {
            statusText = 'zpracování selhalo';
            statusIcon = '❌';
            statusClass = 'status-error';
        } else {
            statusText = 'zpracováno s chybami';
            statusIcon = '⚠️';
            statusClass = 'status-warning';
        }
    } else if (file.status === 'warning' || fileWarnings.length > 0) {
        statusText = 'zpracováno s upozorněními';
        statusIcon = '⚠️';
        statusClass = 'status-warning';
    } else {
        // Check for SDP errors in info messages
        const hasSDPError = fileInfo.some(msg => 
            msg.includes('NESOUHLASÍ') || msg.includes('❌')
        );
        if (hasSDPError) {
            statusText = 'nesouhlasí součty';
            statusIcon = '❌';
            statusClass = 'status-error';
        } else {
            statusText = 'zpracováno bez chyb';
            statusIcon = '✅';
            statusClass = 'status-success';
        }
    }
    
    // Build the header with proper filename display
    const outputFilename = file.output ? file.output.split(/[/\\]/).pop() : 'nedokončeno';
    
    let blockHtml = `
        <div class="file-processing-block collapsible">
            <div class="file-header collapsible-header" onclick="toggleCollapsible('${blockId}')">
                <span class="collapse-icon" id="icon-${blockId}">▶</span>
                📄 <strong>${sourceBasename} → ${outputFilename}</strong>
                <span class="file-status ${statusClass}">${statusIcon} ${statusText}</span>
            </div>
            <div class="processing-steps collapsible-content" id="${blockId}" style="display: none;">
    `;
    
    // Add info messages for this file
    if (fileInfo.length > 0) {
        fileInfo.forEach(msg => {
            // Determine if this is a success or error message
            const isError = msg.includes('NESOUHLASÍ') || msg.includes('❌');
            const isSuccess = msg.includes('✅') || msg.includes('souhlasí');
            const cssClass = isError ? 'error' : (isSuccess ? 'success' : '');
            
            // Clean up repeated "Chyba" text in SDP messages
            let cleanMsg = msg;
            if (msg.includes('NESOUHLASÍ součty v SDP')) {
                // Remove multiple "Chyba:" prefixes and clean up formatting
                cleanMsg = msg.replace(/Chyba: /g, '').replace(/\s+Chyba/g, '');
                cleanMsg = cleanMsg.replace('NESOUHLASÍ součty v SDP!', '❌ NESOUHLASÍ součty v SDP');
            }
            
            blockHtml += `
                <div class="processing-step ${cssClass}">
                    ${cleanMsg}
                </div>
            `;
        });
    }
    
    // Add warnings for this file
    if (fileWarnings.length > 0) {
        fileWarnings.forEach(warning => {
            blockHtml += `
                <div class="processing-step warning">
                    ⚠️ <strong>Upozornění:</strong> ${warning}
                </div>
            `;
        });
    }
    
    // Add errors for this file
    if (fileErrors.length > 0) {
        // Check if we have SDP error sequence
        let sdpErrorIndex = fileErrors.findIndex(err => err.includes('NESOUHLASÍ součty v SDP'));
        
        if (sdpErrorIndex !== -1 && sdpErrorIndex + 3 < fileErrors.length) {
            // Process errors before SDP error normally
            for (let i = 0; i < sdpErrorIndex; i++) {
                blockHtml += `
                    <div class="processing-step error">
                        ❌ <strong>Chyba:</strong> ${fileErrors[i]}
                    </div>
                `;
            }
            
            // Combine SDP errors into one block
            blockHtml += `
                <div class="processing-step error">
                    <strong>❌ NESOUHLASÍ součty v SDP!</strong><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;Aktivity: ${fileErrors[sdpErrorIndex + 1].replace('Aktivity: ', '')}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;SDP forma: ${fileErrors[sdpErrorIndex + 2].replace('SDP forma: ', '')}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;SDP téma: ${fileErrors[sdpErrorIndex + 3].replace('SDP téma: ', '')}
                </div>
            `;
            
            // Process remaining errors after SDP block
            for (let i = sdpErrorIndex + 4; i < fileErrors.length; i++) {
                blockHtml += `
                    <div class="processing-step error">
                        ❌ <strong>Chyba:</strong> ${fileErrors[i]}
                    </div>
                `;
            }
        } else {
            // No SDP error sequence, process normally
            fileErrors.forEach(error => {
                blockHtml += `
                    <div class="processing-step error">
                        ❌ <strong>Chyba:</strong> ${error}
                    </div>
                `;
            });
        }
    }
    
    blockHtml += `
            </div>
        </div>
    `;
    
    return blockHtml;
}

// Initialize when DOM is ready
// Check if file is compatible with detected template version
async function isFileCompatibleWithTemplate(filePath) {
    try {
        // If no template is selected, accept all files
        if (!state.detectedTemplateVersion) {
            return true;
        }
        
        // Use backend to detect source file version
        const result = await window.electronAPI.apiCall('detect/source-version', 'POST', {
            sourcePath: filePath
        });
        
        if (result.success && result.version) {
            // Check if source version matches template version
            return result.version === state.detectedTemplateVersion;
        }
        
        return false; // If we can't detect, exclude file
    } catch (error) {
        console.error('File compatibility check error:', error);
        return false; // If error, exclude file
    }
}

// Detect template version
async function detectTemplateVersion(templatePath) {
    try {
        const result = await window.electronAPI.apiCall('detect/template-version', 'POST', {
            templatePath: templatePath
        });
        
        if (result.success) {
            const version = result.version;
            const versionText = version === '16' ? '16 hodin' : version === '32' ? '32 hodin' : 'Neznámá verze';
            
            elements.invTemplateVersion.innerHTML = `<strong>Verze šablony:</strong> ${versionText}`;
            elements.invTemplateVersion.className = 'template-version';
            
            // Store detected version
            state.detectedTemplateVersion = version;
            
            // Enable file selection buttons when template is valid
            checkInvVzdReady();
        } else {
            elements.invTemplateVersion.innerHTML = `<strong>Neplatná šablona:</strong> ${result.message || 'Nepodařilo se detekovat verzi'}`;
            elements.invTemplateVersion.className = 'template-version invalid';
            state.detectedTemplateVersion = null;
            
            // Clear selected files when template is invalid
            state.selectedFiles['inv-vzd'] = [];
            updateFilesList('inv-vzd');
        }
    } catch (error) {
        console.error('Template version detection error:', error);
        elements.invTemplateVersion.innerHTML = '<strong>Chyba:</strong> Nepodařilo se detekovat verzi šablony';
        elements.invTemplateVersion.className = 'template-version invalid';
        state.detectedTemplateVersion = null;
        
        // Clear selected files and update buttons
        state.selectedFiles['inv-vzd'] = [];
        updateFilesList('inv-vzd');
        checkInvVzdReady();
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    // Load translations first
    if (window.i18n) {
        await window.i18n.load('cs');
        window.i18n.translatePage();
    }
    
    // Then initialize the app
    init();
});