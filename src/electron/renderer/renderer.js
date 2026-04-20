// Renderer process JavaScript

// State management
const state = {
    currentTool: 'welcome',
    selectedFiles: {
        'inv-vzd': [],
        'zor-spec': [],
        'dvpp': [],
        'dvpp-certificates': []
    },
    selectedTemplate: {
        'inv-vzd': null
    },
    selectedFolder: {
        'inv-vzd': null,
        'dvpp': null,
        'dvpp-certificates': null
    },
    dvppMatches: [],
    detectedTemplateVersion: null,
    certificateExtraction: {
        mode: 'gemini',
        importCollapsed: false,
        folderPath: null,
        modelName: 'gemini-3-flash-preview',
        matches: [],
        records: [],
        diagnostics: [],
        rawText: '',
        hasStoredApiKey: false,
        gridApi: null,
        exportMetadata: {
            project_number: '',
            recipient_name: '',
            zor_number: '',
            esf_entry_date: '',
            esf_exit_date: '',
            fill_header: false,
            template_path: 'D:\\JAK2024\\Dokumenty\\Evidence_podpor_poskytnutych_ucastnikum_vzdelavani_MS_ZS_upravene_DVPP.xlsx'
        }
    }
};

// DOM elements
const elements = {
    navItems: document.querySelectorAll('.nav-item'),
    toolContents: document.querySelectorAll('.tool-content'),
    loadingOverlay: document.getElementById('loading-overlay'),
    
    // Inv Vzd elements
    invSelectBtn: document.getElementById('select-inv-files'),
    invFolderBtn: document.getElementById('select-inv-folder'),
    invRefreshBtn: document.getElementById('refresh-inv-folder'),
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

    // DVPP elements
    dvppFolderBtn: document.getElementById('select-dvpp-folder'),
    dvppRefreshBtn: document.getElementById('refresh-dvpp-folder'),
    dvppFolderName: document.getElementById('dvpp-folder-name'),
    dvppFilesList: document.getElementById('dvpp-files-list'),
    dvppSelectAllBtn: document.getElementById('dvpp-select-all'),
    dvppClearSelectionBtn: document.getElementById('dvpp-clear-selection'),
    dvppProcessBtn: document.getElementById('process-dvpp'),
    dvppResults: document.getElementById('dvpp-results'),

    // DVPP certificate extraction elements
    certModeGeminiBtn: document.getElementById('cert-mode-gemini'),
    certModeRawBtn: document.getElementById('cert-mode-raw'),
    certToggleImportPanelBtn: document.getElementById('cert-toggle-import-panel'),
    certImportSection: document.getElementById('cert-import-section'),
    certGeminiPanel: document.getElementById('cert-gemini-panel'),
    certRawPanel: document.getElementById('cert-raw-panel'),
    certPromptsModal: document.getElementById('cert-prompts-modal'),
    certOpenPromptsModalBtn: document.getElementById('open-cert-prompts-modal'),
    certClosePromptsModalBtn: document.getElementById('close-cert-prompts-modal'),
    certApiKeyInput: document.getElementById('cert-gemini-api-key'),
    certRememberKey: document.getElementById('cert-remember-key'),
    certApiKeyStatus: document.getElementById('cert-api-key-status'),
    certLoadStoredKeyBtn: document.getElementById('cert-load-stored-key'),
    certDeleteStoredKeyBtn: document.getElementById('cert-delete-stored-key'),
    certModelSelect: document.getElementById('cert-model-select'),
    certFolderBtn: document.getElementById('select-cert-folder'),
    certFolderRefreshBtn: document.getElementById('refresh-cert-folder'),
    certFolderName: document.getElementById('cert-folder-name'),
    certFilesList: document.getElementById('cert-files-list'),
    certProcessGeminiBtn: document.getElementById('process-cert-gemini'),
    certSystemPrompt: document.getElementById('cert-system-prompt'),
    certUserPrompt: document.getElementById('cert-user-prompt'),
    certCopySystemPromptBtn: document.getElementById('copy-cert-system-prompt'),
    certCopyUserPromptBtn: document.getElementById('copy-cert-user-prompt'),
    certRawText: document.getElementById('cert-raw-text'),
    certProcessRawBtn: document.getElementById('process-cert-raw'),
    certClearRawTextBtn: document.getElementById('clear-cert-raw-text'),
    certBulkTemplateSelect: document.getElementById('cert-bulk-template-select'),
    certApplyTemplateAllBtn: document.getElementById('cert-apply-template-all'),
    certBulkFormaSelect: document.getElementById('cert-bulk-forma-select'),
    certApplyFormaAllBtn: document.getElementById('cert-apply-forma-all'),
    certBulkPohlaviSelect: document.getElementById('cert-bulk-pohlavi-select'),
    certApplyPohlaviAllBtn: document.getElementById('cert-apply-pohlavi-all'),
    certRecordsTable: document.getElementById('cert-records-table'),
    certDiagnostics: document.getElementById('cert-diagnostics'),
    certProjectNumber: document.getElementById('cert-project-number'),
    certRecipientName: document.getElementById('cert-recipient-name'),
    certZorNumber: document.getElementById('cert-zor-number'),
    certEsfEntryDate: document.getElementById('cert-esf-entry-date'),
    certEsfExitDate: document.getElementById('cert-esf-exit-date'),
    certFillHeader: document.getElementById('cert-fill-header'),
    certTemplatePath: document.getElementById('cert-template-path'),
    certSelectTemplateBtn: document.getElementById('select-cert-template'),
    certCopyTsvBtn: document.getElementById('copy-cert-tsv'),
    certSaveTsvBtn: document.getElementById('save-cert-tsv'),
    certSaveExcelBtn: document.getElementById('save-cert-excel'),
    certSaveEsfBtn: document.getElementById('save-cert-esf'),
    certResults: document.getElementById('cert-results'),

    // Plakat elements
    plakatForm: document.getElementById('plakat-form'),
    plakatResults: document.getElementById('plakat-results')
};

const CERT_SYSTEM_PROMPT = `### ROLE A CÍL ###
Jsi "Certifikátor v2.1", ultra-přesný AI asistent specializovaný na OCR extrakci dat z certifikátů a osvědčení o dalším vzdělávání pedagogických pracovníků (DVPP). Tvým jediným cílem je bezchybně extrahovat klíčové údaje z dodaných dokumentů a zformátovat je pro přímé vložení do tabulkového procesoru.

### KLÍČOVÝ KONTEXT A ZNALOSTI ###
* Jsi expert na terminologii v oblasti českého školství a DVPP.
* Rozumíš kontextu českých jmen a příjmení a jejich skloňování.
* Přiřazení kategorie "Téma" se řídí výhradně následujícím závazným číselníkem. Musíš dodržet přesné znění a malá písmena.

**ZÁVAZNÝ ČÍSELNÍK TÉMAT:**
* pedagogická diagnostika, individualizace vzdělávání, formativní hodnocení, podpora nadání/talentu, řečová výchova, grafomotorika, rozvoj gramotností, rozvoj digitálních kompetencí, podpora polytechniky, vzdělávání pro udržitelný rozvoj – např. EVVO, klimatické vzdělávání, principy místně zakotveného učení, well-being a psychohygiena, genderová tematika v obsahu vzdělávání, výuka moderních dějin, mediální gramotnost, prevence kyberšikany, chování na sociálních sítích, umělá inteligence, pohybové aktivity, práce s dětmi/žáky se speciálními vzdělávacími potřebami; vzdělávání heterogenních kolektivů, vzdělávání dětí/žáků cizinců a dětí/žáků s potřebou jazykové podpory, rozvoj pedagogických kompetencí v oblasti metod a forem vzdělávání, komunikace se zákonnými zástupci, management škol, řízení organizace, leadership a řízení pedagogického procesu, vzdělávání dětí a žáků z marginalizovaných skupin, jako jsou Romové, podpora uvádějících/provázejících učitelů, profesní rozvoj ostatních pracovníků ve vzdělávání

### ZÁSADY KOMUNIKACE ###
* Styl: Strojový, datově orientovaný. Žádné pozdravy, úvody ani komentáře.
* Tón: Absolutně neutrální a objektivní.

### OMEZENÍ, PRAVIDLA A LOGIKA ZPRACOVÁNÍ ###
* Dávkové zpracování: Pokud obdržíš více souborů najednou nebo vícestránkový dokument, považuj každý certifikát za samostatnou položku.
* Nejistota: Pokud si jakýmkoli údajem nejsi jistý na 100 %, připoj za něj otazník.
* Logika pro pole 'Téma': Pole vyplňuj pouze hodnotou ze závazného číselníku a jen při jistotě nad 90 %.
* Logika pro pole 'Datum ukončení vzdělávání': Pokud je vzdělávání více dnů, použij nejvyšší datum.
* Striktní formát: Dodrž skutečné tabulátory.`;

const CERT_USER_PROMPT = `Proveď extrakci dat z následujícího textu nebo dokumentů. Zaměř se na identifikaci certifikátů nebo osvědčení o absolvování kurzů.
Formát výstupu: čistý raw text.
Pro každý certifikát vygeneruj jeden samostatný řádek bez nadpisů a markdownu.
Struktura polí:
Příjmení<TAB>Jméno<TAB>Datum narození<TAB>Název kurzu<TAB>Datum ukončení vzdělávání<TAB>Počet hodin<TAB><TAB>Téma
Vynech tituly.
Datum narození i datum ukončení musí být ve tvaru dd.mm.yyyy.
Finální výstup vlož do jednoho bloku kódu \`\`\`text.`;

const TEMPLATE_OPTIONS = [
    'vzdělávání MŠ_2_I_5',
    'vzdělávání ZŠ_2_II_4',
    'vzdělávání ŠD_SK_2_V_1',
    'vzdělávání SVČ_2_V_1',
    'vzdělávání ZUŠ_2_VII_1'
];

const FORMA_OPTIONS = [
    'akreditovaný kurz průběžné DVPP',
    'neakreditovaný kurz',
    'kvalifikační_studium_DVPP',
    'akreditovaný kurz jiný',
    'stáž',
    'mentoring',
    'supevize',
    'koučink'
];

const POHLAVI_OPTIONS = [
    'POHZENY',
    'POHMUZI'
];

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
    elements.invRefreshBtn.addEventListener('click', refreshInvFolder);
    
    // Initially disable file selection buttons until template is selected
    elements.invSelectBtn.disabled = true;
    elements.invFolderBtn.disabled = true;
    elements.zorSelectBtn.addEventListener('click', () => selectFiles('zor-spec'));
    elements.zorFolderBtn.addEventListener('click', selectZorFolder);
    elements.invTemplateBtn.addEventListener('click', selectInvTemplate);
    
    // Setup process buttons
    elements.invProcessBtn.addEventListener('click', processInvVzd);
    elements.zorProcessBtn.addEventListener('click', processZorSpec);
    elements.dvppFolderBtn.addEventListener('click', selectDvppFolder);
    elements.dvppRefreshBtn.addEventListener('click', refreshDvppFolder);
    elements.dvppSelectAllBtn.addEventListener('click', () => setDvppSelection(true));
    elements.dvppClearSelectionBtn.addEventListener('click', () => setDvppSelection(false));
    elements.dvppProcessBtn.addEventListener('click', processDvppReport);

    elements.certModeGeminiBtn.addEventListener('click', () => switchCertificateMode('gemini'));
    elements.certModeRawBtn.addEventListener('click', () => switchCertificateMode('raw'));
    elements.certToggleImportPanelBtn.addEventListener('click', toggleCertificateImportPanel);
    elements.certOpenPromptsModalBtn.addEventListener('click', openCertificatePromptsModal);
    elements.certClosePromptsModalBtn.addEventListener('click', closeCertificatePromptsModal);
    elements.certLoadStoredKeyBtn.addEventListener('click', loadStoredGeminiApiKey);
    elements.certDeleteStoredKeyBtn.addEventListener('click', deleteStoredGeminiApiKey);
    elements.certFolderBtn.addEventListener('click', selectCertificateFolder);
    elements.certFolderRefreshBtn.addEventListener('click', refreshCertificateFolder);
    elements.certProcessGeminiBtn.addEventListener('click', processCertificatesWithGemini);
    elements.certProcessRawBtn.addEventListener('click', processCertificatesFromRawText);
    elements.certClearRawTextBtn.addEventListener('click', clearCertificateRawText);
    elements.certCopySystemPromptBtn.addEventListener('click', () => copyTextToClipboard(CERT_SYSTEM_PROMPT, 'Systemový prompt byl zkopírován.'));
    elements.certCopyUserPromptBtn.addEventListener('click', () => copyTextToClipboard(CERT_USER_PROMPT, 'Uživatelský prompt byl zkopírován.'));
    elements.certCopyTsvBtn.addEventListener('click', copyCertificateTsv);
    elements.certSaveTsvBtn.addEventListener('click', saveCertificateTsv);
    elements.certSaveExcelBtn.addEventListener('click', saveCertificateExcel);
    elements.certSaveEsfBtn.addEventListener('click', saveCertificateEsfImport);
    elements.certApplyTemplateAllBtn.addEventListener('click', applyCertificateTemplateToAllRecords);
    elements.certApplyFormaAllBtn.addEventListener('click', applyCertificateFormaToAllRecords);
    elements.certApplyPohlaviAllBtn.addEventListener('click', applyCertificatePohlaviToAllRecords);
    elements.certSelectTemplateBtn.addEventListener('click', selectCertificateTemplate);
    elements.certModelSelect.addEventListener('change', (event) => {
        state.certificateExtraction.modelName = event.target.value;
    });
    elements.certPromptsModal.addEventListener('click', (event) => {
        if (event.target === elements.certPromptsModal) {
            closeCertificatePromptsModal();
        }
    });
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && !elements.certPromptsModal.hidden) {
            closeCertificatePromptsModal();
        }
    });
    bindSharedResultInteractionHandlers();
    bindCertificateInteractionHandlers();
    bindCertificateMetadataInputs();
    createCertificateGrid();
    
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
    elements.certSystemPrompt.value = CERT_SYSTEM_PROMPT;
    elements.certUserPrompt.value = CERT_USER_PROMPT;
    elements.certProjectNumber.value = state.certificateExtraction.exportMetadata.project_number;
    elements.certRecipientName.value = state.certificateExtraction.exportMetadata.recipient_name;
    elements.certZorNumber.value = state.certificateExtraction.exportMetadata.zor_number;
    elements.certEsfEntryDate.value = state.certificateExtraction.exportMetadata.esf_entry_date;
    elements.certEsfExitDate.value = state.certificateExtraction.exportMetadata.esf_exit_date;
    elements.certFillHeader.checked = !!state.certificateExtraction.exportMetadata.fill_header;
    elements.certTemplatePath.value = state.certificateExtraction.exportMetadata.template_path;
    setCertificateImportCollapsed(false);
    await refreshGeminiApiKeyStatus();
    await autoLoadStoredGeminiApiKey();
    renderCertificateFilesList();
    updateCertificateActions();
    
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
                    // Check if ready to process (validates version compatibility)
                    checkZorSpecReady();
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
                        <button
                            class="btn-remove"
                            type="button"
                            data-action="remove-file"
                            data-tool="${escapeHtml(tool)}"
                            data-file-path="${escapeHtml(file)}"
                        >✕</button>
                    </div>
                `;
            } else {
                fileDiv.innerHTML = `
                    <div class="file-item-content">
                        <div class="file-path">
                            <strong>Cesta:</strong> ${wslToWindowsPath(file)}
                        </div>
                        <button
                            class="btn-remove"
                            type="button"
                            data-action="remove-file"
                            data-tool="${escapeHtml(tool)}"
                            data-file-path="${escapeHtml(file)}"
                        >✕</button>
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
            // Store folder path for refresh
            state.selectedFolder['inv-vzd'] = folderPath;

            // Scan folder for Excel files
            const suitableFiles = await scanFolderForAttendanceFiles(folderPath);

            if (suitableFiles.length > 0) {
                state.selectedFiles['inv-vzd'] = suitableFiles;
                updateFilesList('inv-vzd');
                checkInvVzdReady();
                // Show refresh button
                elements.invRefreshBtn.style.display = 'inline-block';
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

// Refresh folder - rescan for attendance files
async function refreshInvFolder() {
    const folderPath = state.selectedFolder['inv-vzd'];
    if (!folderPath) {
        showMessage('Není vybrána žádná složka k obnovení', 'warning');
        return;
    }

    try {
        // Clear current files
        state.selectedFiles['inv-vzd'] = [];
        updateFilesList('inv-vzd');

        // Rescan folder
        const suitableFiles = await scanFolderForAttendanceFiles(folderPath);

        if (suitableFiles.length > 0) {
            state.selectedFiles['inv-vzd'] = suitableFiles;
            updateFilesList('inv-vzd');
            checkInvVzdReady();
            showMessage(`Obnoveno: Nalezeno ${suitableFiles.length} vhodných souborů docházky`, 'success');
        } else {
            elements.invRefreshBtn.style.display = 'none';
            showMessage('Ve složce nejsou žádné vhodné soubory docházky', 'warning');
        }
    } catch (error) {
        console.error('Folder refresh error:', error);
        showMessage('Chyba při obnovování seznamu', 'error');
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

                updateFilesList('zor-spec');

                // Check if ready to process (validates version compatibility)
                checkZorSpecReady();

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

// Check if Zor Spec is ready to process
function checkZorSpecReady() {
    const hasFiles = state.selectedFiles['zor-spec'].length > 0;

    if (!hasFiles) {
        elements.zorProcessBtn.disabled = true;
        // Clear any version error message
        const errorMsg = document.getElementById('zor-version-error');
        if (errorMsg) errorMsg.remove();
        return;
    }

    // Detect mixed versions (16h and 32h)
    const versionCheck = detectMixedVersions(state.selectedFiles['zor-spec']);

    if (versionCheck.mixed) {
        // Show error message
        showZorVersionError(versionCheck);
        elements.zorProcessBtn.disabled = true;
    } else {
        // Clear error message and enable processing
        const errorMsg = document.getElementById('zor-version-error');
        if (errorMsg) errorMsg.remove();
        elements.zorProcessBtn.disabled = false;
    }
}

function checkDvppReady() {
    const hasFolder = !!state.selectedFolder['dvpp'];
    const selectedCount = state.selectedFiles['dvpp'].length;
    const hasMatches = state.dvppMatches.length > 0;

    elements.dvppProcessBtn.disabled = !(hasFolder && selectedCount > 0);
    elements.dvppSelectAllBtn.disabled = !hasMatches;
    elements.dvppClearSelectionBtn.disabled = !hasMatches;
}

async function selectDvppFolder() {
    try {
        const folderPath = await window.electronAPI.selectFolder({
            configKey: 'lastDvppFolder',
            title: 'Vyberte projektovou složku pro DVPP report'
        });

        if (folderPath) {
            state.selectedFolder['dvpp'] = folderPath;
            elements.dvppFolderName.innerHTML = `
                <div class="template-path">
                    <strong>Cesta:</strong> ${wslToWindowsPath(folderPath)}
                </div>
            `;

            showLoading(true, {
                text: 'Hledám DVPP soubory v projektové složce...'
            });
            setStatusMessage('Prohledávám projektovou složku pro DVPP soubory...');

            await loadDvppMatches(folderPath);
            showLoading(false);
            elements.dvppRefreshBtn.style.display = 'inline-block';
        }
    } catch (error) {
        showLoading(false);
        console.error('DVPP folder selection error:', error);
        showMessage('Chyba při výběru projektové složky', 'error');
        setStatusMessage('Výběr projektové složky selhal', 4000);
    }
}

async function refreshDvppFolder() {
    const folderPath = state.selectedFolder['dvpp'];
    if (!folderPath) {
        showMessage('Není vybrána žádná projektová složka', 'warning');
        return;
    }

    try {
        showLoading(true, {
            text: 'Obnovuji seznam DVPP souborů...'
        });
        setStatusMessage('Znovu prohledávám projektovou složku...');
        await loadDvppMatches(folderPath);
        showLoading(false);
    } catch (error) {
        showLoading(false);
        console.error('DVPP folder refresh error:', error);
        showMessage('Chyba při obnovování DVPP seznamu', 'error');
        setStatusMessage('Obnovení DVPP seznamu selhalo', 4000);
    }
}

async function loadDvppMatches(folderPath) {
    const result = await window.electronAPI.apiCall('scan/dvpp-directory', 'POST', {
        projectDir: folderPath
    });

    state.dvppMatches = result.matches || [];
    state.selectedFiles['dvpp'] = state.dvppMatches.map(match => match.file_path);
    renderDvppFilesList();
    checkDvppReady();

    if (state.dvppMatches.length > 0) {
        showMessage(`Nalezeno ${state.dvppMatches.length} vhodných DVPP souborů`, 'success');
        setStatusMessage(`Nalezeno ${state.dvppMatches.length} DVPP souborů`, 4000);
    } else {
        showMessage('Ve vybrané složce nebyly nalezeny žádné vhodné DVPP soubory', 'warning');
        setStatusMessage('Nebyly nalezeny žádné vhodné DVPP soubory', 4000);
    }
}

function renderDvppFilesList() {
    elements.dvppFilesList.innerHTML = '';

    if (state.dvppMatches.length === 0) {
        elements.dvppFilesList.innerHTML = '<p class="file-item">Žádné DVPP soubory nebyly nalezeny</p>';
        return;
    }

    state.dvppMatches.forEach((match, index) => {
        const fileDiv = document.createElement('div');
        fileDiv.className = 'file-item dvpp-file-item';

        const isChecked = state.selectedFiles['dvpp'].includes(match.file_path);
        const reportInfo = match.report_number ? `ZoR ${match.report_number}` : 'ZoR neuvedeno';

        fileDiv.innerHTML = `
            <label class="checkbox-row">
                <input
                    type="checkbox"
                    class="dvpp-checkbox"
                    ${isChecked ? 'checked' : ''}
                    data-action="toggle-dvpp-file"
                    data-file-path="${escapeHtml(match.file_path)}"
                >
                <div class="checkbox-row-content">
                    <div class="file-path">
                        <strong>${index + 1}. ${match.relative_path}</strong>
                    </div>
                    <div class="dvpp-file-meta">
                        <span>${reportInfo}</span>
                        <span>${match.participant_count} účastníků</span>
                        <span>List: ${match.sheet_name}</span>
                    </div>
                </div>
            </label>
        `;

        elements.dvppFilesList.appendChild(fileDiv);
    });
}

function toggleDvppFile(filePath, checked) {
    const selected = state.selectedFiles['dvpp'];
    const index = selected.indexOf(filePath);

    if (checked && index === -1) {
        selected.push(filePath);
    }

    if (!checked && index !== -1) {
        selected.splice(index, 1);
    }

    checkDvppReady();
}

function setDvppSelection(selectAll) {
    state.selectedFiles['dvpp'] = selectAll ? state.dvppMatches.map(match => match.file_path) : [];
    renderDvppFilesList();
    checkDvppReady();
}

async function processDvppReport() {
    try {
        showLoading(true);
        setStatusMessage('Generuji DVPP report...');

        const result = await window.electronAPI.apiCall('process/dvpp-report', 'POST', {
            projectDir: state.selectedFolder['dvpp'],
            filePaths: state.selectedFiles['dvpp']
        });

        showLoading(false);

        if (result.status === 'success') {
            const reportPath = wslToWindowsPath(result.data.report_path);
            const processedFiles = result.data.selected_files || [];
            const reportCount = (result.data.report_numbers || []).length;

            let resultHtml = `
                <div class="status-banner">
                    <div class="status-content">
                        <div class="status-icon">✓</div>
                        <div class="status-text">
                            <h3>DVPP report vygenerován</h3>
                            <p>HTML report byl uložen do projektové složky a je připraven k otevření.</p>
                        </div>
                    </div>
                </div>

                <div class="stats-grid dvpp-stats">
                    <div class="stat-card">
                        <div class="stat-content">
                            <div class="stat-header">
                                <div class="stat-label">ZPRACOVANÉ SOUBORY</div>
                            </div>
                            <div class="stat-value">${result.data.files_processed}</div>
                        </div>
                        <div class="stat-icon">📄</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-content">
                            <div class="stat-header">
                                <div class="stat-label">UNIKÁTNÍ PEDAGOGOVÉ</div>
                            </div>
                            <div class="stat-value">${result.data.unique_participants}</div>
                        </div>
                        <div class="stat-icon">👥</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-content">
                            <div class="stat-header">
                                <div class="stat-label">ZAHRNUTÉ ZOR</div>
                            </div>
                            <div class="stat-value">${reportCount}</div>
                        </div>
                        <div class="stat-icon">📚</div>
                    </div>
                </div>

                <div class="output-section">
                    <h4>Výstupní report</h4>
                    <p>
                        <a href="#" class="file-link" data-action="open-file" data-file-path="${escapeHtml(reportPath)}">
                            ${result.data.report_filename}
                        </a>
                    </p>
                </div>
            `;

            if (processedFiles.length > 0) {
                resultHtml += `
                    <div class="output-section">
                        <h4>Zpracované soubory</h4>
                        <ul class="info-messages">
                            ${processedFiles.map(file => `<li>${file}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }

            elements.dvppResults.innerHTML = resultHtml;
            elements.dvppResults.classList.add('show');
            showMessage(`DVPP report uložen: ${result.data.report_filename}`, 'success');
        } else {
            let errorHtml = `
                <h3 class="error">Zpracování selhalo ❌</h3>
                <p><strong>Hlavní zpráva:</strong> ${result.message || 'Neznámá chyba'}</p>
            `;

            if (result.errors && result.errors.length > 0) {
                errorHtml += '<h4>Detailní chyby:</h4><ul class="error-messages">';
                result.errors.forEach(error => {
                    errorHtml += `<li class="error-item">${error}</li>`;
                });
                errorHtml += '</ul>';
            }

            elements.dvppResults.innerHTML = errorHtml;
            elements.dvppResults.classList.add('show');
        }
    } catch (error) {
        showLoading(false);
        console.error('DVPP processing error:', error);
        showMessage('Chyba při generování DVPP reportu: ' + error.message, 'error');
    }
}

function switchCertificateMode(mode) {
    state.certificateExtraction.mode = mode;
    elements.certModeGeminiBtn.classList.toggle('active', mode === 'gemini');
    elements.certModeGeminiBtn.classList.toggle('btn-success', mode === 'gemini');
    elements.certModeGeminiBtn.classList.toggle('btn-secondary', mode !== 'gemini');
    elements.certModeRawBtn.classList.toggle('active', mode === 'raw');
    elements.certModeRawBtn.classList.toggle('btn-primary', mode === 'raw');
    elements.certModeRawBtn.classList.toggle('btn-secondary', mode !== 'raw');
    if (state.certificateExtraction.importCollapsed) {
        setCertificateImportCollapsed(false);
        return;
    }
    syncCertificateImportPanels();
}

function openCertificatePromptsModal() {
    elements.certPromptsModal.hidden = false;
}

function closeCertificatePromptsModal() {
    elements.certPromptsModal.hidden = true;
}

function clearCertificateRawText() {
    elements.certRawText.value = '';
    state.certificateExtraction.rawText = '';
    elements.certRawText.focus();
}

function syncCertificateImportPanels() {
    const importVisible = !state.certificateExtraction.importCollapsed;
    elements.certImportSection.classList.toggle('collapsed', !importVisible);
    elements.certGeminiPanel.classList.toggle('active', importVisible && state.certificateExtraction.mode === 'gemini');
    elements.certRawPanel.classList.toggle('active', importVisible && state.certificateExtraction.mode === 'raw');
    elements.certToggleImportPanelBtn.textContent = 'Zobrazit import';
    elements.certToggleImportPanelBtn.disabled = importVisible;
}

function setCertificateImportCollapsed(collapsed) {
    state.certificateExtraction.importCollapsed = !!collapsed;
    syncCertificateImportPanels();
}

function toggleCertificateImportPanel() {
    if (state.certificateExtraction.importCollapsed) {
        setCertificateImportCollapsed(false);
    }
}

function resetCertificateExtractionOutput() {
    state.certificateExtraction.records = [];
    state.certificateExtraction.diagnostics = [];
    refreshCertificateGridRows();
    renderCertificateDiagnostics();
    updateCertificateActions();
}

function bindCertificateMetadataInputs() {
    const bindings = [
        ['project_number', elements.certProjectNumber],
        ['recipient_name', elements.certRecipientName],
        ['zor_number', elements.certZorNumber],
        ['esf_entry_date', elements.certEsfEntryDate],
        ['esf_exit_date', elements.certEsfExitDate],
        ['template_path', elements.certTemplatePath]
    ];

    bindings.forEach(([key, input]) => {
        input.addEventListener('input', (event) => {
            state.certificateExtraction.exportMetadata[key] = event.target.value;
        });
    });

    elements.certFillHeader.addEventListener('change', (event) => {
        state.certificateExtraction.exportMetadata.fill_header = !!event.target.checked;
    });
}

async function refreshGeminiApiKeyStatus() {
    try {
        const result = await window.electronAPI.getGeminiApiKeyStatus();
        state.certificateExtraction.hasStoredApiKey = !!(result && result.stored);
        elements.certRememberKey.checked = state.certificateExtraction.hasStoredApiKey;
        elements.certApiKeyStatus.textContent = state.certificateExtraction.hasStoredApiKey
            ? 'Uložený Gemini API key je k dispozici v zabezpečeném úložišti.'
            : 'Zatím není uložen žádný Gemini API key.';
    } catch (error) {
        console.error('Gemini key status error:', error);
        elements.certApiKeyStatus.textContent = 'Nepodařilo se ověřit stav uloženého Gemini API klíče.';
    }
}

async function loadStoredGeminiApiKey() {
    try {
        const apiKey = await window.electronAPI.getGeminiApiKey();
        if (!apiKey) {
            showMessage('V zabezpečeném úložišti není uložen žádný Gemini API key.', 'warning');
            return;
        }
        elements.certApiKeyInput.value = apiKey;
        elements.certRememberKey.checked = true;
        showMessage('Uložený Gemini API key byl načten.', 'success');
    } catch (error) {
        console.error('Load stored Gemini key error:', error);
        showMessage('Nepodařilo se načíst uložený Gemini API key.', 'error');
    }
}

async function autoLoadStoredGeminiApiKey() {
    if (!state.certificateExtraction.hasStoredApiKey) {
        return;
    }

    try {
        const apiKey = await window.electronAPI.getGeminiApiKey();
        if (!apiKey) {
            return;
        }
        elements.certApiKeyInput.value = apiKey;
        elements.certRememberKey.checked = true;
    } catch (error) {
        console.error('Auto-load stored Gemini key error:', error);
    }
}

async function deleteStoredGeminiApiKey() {
    try {
        await window.electronAPI.deleteGeminiApiKey();
        elements.certApiKeyInput.value = '';
        elements.certRememberKey.checked = false;
        await refreshGeminiApiKeyStatus();
        showMessage('Uložený Gemini API key byl odstraněn.', 'success');
    } catch (error) {
        console.error('Delete stored Gemini key error:', error);
        showMessage('Nepodařilo se odstranit uložený Gemini API key.', 'error');
    }
}

async function resolveGeminiApiKey() {
    const typedKey = elements.certApiKeyInput.value.trim();
    if (typedKey) {
        if (elements.certRememberKey.checked) {
            await window.electronAPI.saveGeminiApiKey(typedKey);
            await refreshGeminiApiKeyStatus();
        }
        return typedKey;
    }

    if (state.certificateExtraction.hasStoredApiKey) {
        return await window.electronAPI.getGeminiApiKey();
    }

    throw new Error('Zadejte Gemini API key nebo použijte uložený klíč.');
}

async function selectCertificateFolder() {
    try {
        const folderPath = await window.electronAPI.selectFolder({
            configKey: 'lastDvppCertificateFolder',
            title: 'Vyberte složku s certifikáty DVPP'
        });

        if (!folderPath) {
            return;
        }

        state.certificateExtraction.folderPath = folderPath;
        state.selectedFolder['dvpp-certificates'] = folderPath;
        elements.certFolderName.textContent = wslToWindowsPath(folderPath);
        showLoading(true, { text: 'Načítám certifikáty ve vybrané složce...' });
        await loadCertificateMatches(folderPath);
        showLoading(false);
        elements.certFolderRefreshBtn.style.display = 'inline-block';
    } catch (error) {
        showLoading(false);
        console.error('Certificate folder selection error:', error);
        showMessage('Chyba při výběru složky s certifikáty.', 'error');
    }
}

async function refreshCertificateFolder() {
    if (!state.certificateExtraction.folderPath) {
        showMessage('Není vybraná žádná složka s certifikáty.', 'warning');
        return;
    }

    try {
        showLoading(true, { text: 'Obnovuji seznam certifikátů...' });
        elements.certFolderName.textContent = wslToWindowsPath(state.certificateExtraction.folderPath);
        await loadCertificateMatches(state.certificateExtraction.folderPath);
        showLoading(false);
    } catch (error) {
        showLoading(false);
        console.error('Certificate folder refresh error:', error);
        showMessage(`Chyba při načítání certifikátů: ${error.message}`, 'error');
    }
}

async function loadCertificateMatches(folderPath) {
    const result = await window.electronAPI.apiCall('dvpp-certificates/scan', 'POST', {
        folderPath
    });

    state.certificateExtraction.matches = result.matches || [];
    state.selectedFiles['dvpp-certificates'] = state.certificateExtraction.matches.map((match) => match.file_path);
    renderCertificateFilesList();
    updateCertificateActions();

    if (state.certificateExtraction.matches.length > 0) {
        showMessage(`Nalezeno ${state.certificateExtraction.matches.length} podporovaných certifikátů.`, 'success');
    } else {
        showMessage('Ve vybrané složce nebyly nalezeny žádné podporované certifikáty.', 'warning');
    }
}

function renderCertificateFilesList() {
    elements.certFilesList.innerHTML = '';

    if (!state.certificateExtraction.folderPath) {
        elements.certFilesList.innerHTML = '<p class="file-item">Nejprve vyberte složku s certifikáty.</p>';
        return;
    }

    if (state.certificateExtraction.matches.length === 0) {
        elements.certFilesList.innerHTML = '<p class="file-item">Žádné podporované soubory PDF/JPG/JPEG/PNG nebyly nalezeny.</p>';
        return;
    }

    state.certificateExtraction.matches.forEach((match, index) => {
        const fileDiv = document.createElement('div');
        fileDiv.className = 'file-item dvpp-file-item';
        const isChecked = state.selectedFiles['dvpp-certificates'].includes(match.file_path);

        fileDiv.innerHTML = `
            <label class="checkbox-row">
                <input
                    type="checkbox"
                    class="dvpp-checkbox"
                    data-cert-file-path="${escapeHtml(match.file_path)}"
                    ${isChecked ? 'checked' : ''}
                >
                <div class="checkbox-row-content">
                    <div class="file-path">
                        <strong>${index + 1}. ${escapeHtml(match.relative_path)}</strong>
                    </div>
                    <div class="dvpp-file-meta">
                        <span>${escapeHtml(wslToWindowsPath(match.file_path))}</span>
                    </div>
                </div>
            </label>
        `;

        elements.certFilesList.appendChild(fileDiv);
    });
}

function toggleCertificateFile(filePath, checked) {
    const selected = state.selectedFiles['dvpp-certificates'];
    const index = selected.indexOf(filePath);

    if (checked && index === -1) {
        selected.push(filePath);
    }

    if (!checked && index !== -1) {
        selected.splice(index, 1);
    }

    updateCertificateActions();
}

async function processCertificatesWithGemini() {
    try {
        const apiKey = await resolveGeminiApiKey();
        resetCertificateExtractionOutput();
        showLoading(true, { text: 'Vytěžuji certifikáty přes Gemini...' });
        setStatusMessage('Probíhá vytěžování certifikátů přes Gemini...');

        const result = await window.electronAPI.apiCall('dvpp-certificates/import/gemini', 'POST', {
            folderPath: state.certificateExtraction.folderPath,
            selectedFiles: state.selectedFiles['dvpp-certificates'],
            modelName: state.certificateExtraction.modelName,
            apiKey
        });

        showLoading(false);
        applyCertificateBatchResult(result.data.batch, result.data.diagnostics || []);
        showMessage(`Vytěženo ${state.certificateExtraction.records.length} certifikátů.`, 'success');
    } catch (error) {
        showLoading(false);
        console.error('Gemini certificate import error:', error);
        if (error.data && error.data.batch) {
            applyCertificateBatchResult(error.data.batch, error.data.diagnostics || []);
        }
        showMessage(`Chyba při vytěžování certifikátů: ${error.message}`, 'error');
    }
}

async function processCertificatesFromRawText() {
    try {
        const rawText = elements.certRawText.value.trim();
        if (!rawText) {
            showMessage('Vložte raw text z Google AI Studia.', 'warning');
            return;
        }

        resetCertificateExtractionOutput();
        showLoading(true, { text: 'Načítám raw text certifikátů...' });
        const result = await window.electronAPI.apiCall('dvpp-certificates/import/raw-text', 'POST', {
            rawText
        });
        showLoading(false);

        applyCertificateBatchResult(result.data.batch, []);
        showMessage(`Načteno ${state.certificateExtraction.records.length} certifikátů z raw textu.`, 'success');
    } catch (error) {
        showLoading(false);
        console.error('Raw text certificate import error:', error);
        showMessage(`Chyba při načítání raw textu: ${error.message}`, 'error');
    }
}

function applyCertificateBatchResult(batch, diagnostics) {
    state.certificateExtraction.records = Array.isArray(batch.records) ? batch.records : [];
    state.certificateExtraction.diagnostics = diagnostics;
    if (state.certificateExtraction.records.length > 0) {
        setCertificateImportCollapsed(true);
    }
    refreshCertificateGridRows();
    renderCertificateDiagnostics();
    updateCertificateActions();
}

function buildCertificateGridRowData() {
    return state.certificateExtraction.records.map((record, index) => ({
        __recordIndex: index,
        surname: record.working_record.surname || '',
        name: record.working_record.name || '',
        birth_date: record.working_record.birth_date || '',
        sablona: record.working_record.sablona || '',
        course_name: record.working_record.course_name || '',
        completion_date: record.working_record.completion_date || '',
        hours: record.working_record.hours || '',
        forma: record.working_record.forma || '',
        pohlavi: record.working_record.pohlavi || '',
        topic: record.working_record.topic || ''
    }));
}

function ensureCertificateGridApi() {
    if (state.certificateExtraction.gridApi) {
        return state.certificateExtraction.gridApi;
    }

    return createCertificateGrid();
}

function createCertificateGrid() {
    if (state.certificateExtraction.gridApi) {
        return state.certificateExtraction.gridApi;
    }

    if (!window.agGrid || typeof window.agGrid.createGrid !== 'function') {
        console.error('AG Grid is not available in the renderer process.');
        elements.certRecordsTable.className = 'cert-records-table empty-state';
        elements.certRecordsTable.textContent = 'Editor certifikátů se nepodařilo načíst.';
        return null;
    }

    elements.certRecordsTable.className = 'cert-records-table ag-theme-alpine';
    elements.certRecordsTable.innerHTML = '';

    const gridOptions = {
        rowData: buildCertificateGridRowData(),
        theme: 'legacy',
        domLayout: 'autoHeight',
        defaultColDef: {
            editable: true,
            resizable: true,
            sortable: false,
            suppressMovable: true,
            wrapHeaderText: true,
            autoHeaderHeight: true,
            flex: 1,
            minWidth: 130
        },
        animateRows: true,
        singleClickEdit: true,
        stopEditingWhenCellsLoseFocus: true,
        overlayNoRowsTemplate: '<span class="cert-grid-empty">Zatím nejsou načtené žádné certifikáty.</span>',
        columnDefs: [
            { field: 'surname', headerName: 'Příjmení', minWidth: 150 },
            { field: 'name', headerName: 'Jméno', minWidth: 140 },
            { field: 'birth_date', headerName: 'Datum narození', minWidth: 150 },
            {
                field: 'sablona',
                headerName: 'Šablona',
                minWidth: 220,
                cellEditor: 'agSelectCellEditor',
                cellEditorParams: { values: TEMPLATE_OPTIONS },
                cellClass: 'cert-grid-template-cell'
            },
            { field: 'course_name', headerName: 'Název kurzu', minWidth: 260, flex: 1.6 },
            { field: 'completion_date', headerName: 'Datum ukončení', minWidth: 150 },
            { field: 'hours', headerName: 'Hodiny', minWidth: 110 },
            {
                field: 'forma',
                headerName: 'Forma',
                minWidth: 220,
                cellEditor: 'agSelectCellEditor',
                cellEditorParams: { values: FORMA_OPTIONS },
                cellClass: 'cert-grid-forma-cell'
            },
            {
                field: 'pohlavi',
                headerName: 'Pohlaví',
                minWidth: 140,
                cellEditor: 'agSelectCellEditor',
                cellEditorParams: { values: POHLAVI_OPTIONS }
            },
            { field: 'topic', headerName: 'Téma', minWidth: 220, flex: 1.4 },
            {
                colId: 'actions',
                headerName: '',
                editable: false,
                minWidth: 84,
                maxWidth: 84,
                pinned: 'right',
                lockPinned: true,
                cellRenderer: () => '<button type="button" class="cert-grid-remove-btn" data-cert-grid-remove="1" aria-label="Odstranit záznam">✕</button>'
            }
        ],
        onCellValueChanged: (event) => {
            if (!event.colDef.field) {
                return;
            }
            updateCertificateField(event.data.__recordIndex, event.colDef.field, event.newValue ?? '');
        },
        onCellClicked: (event) => {
            if (event.column.getColId() !== 'actions') {
                return;
            }
            removeCertificateRecord(event.data.__recordIndex);
        }
    };

    state.certificateExtraction.gridApi = window.agGrid.createGrid(elements.certRecordsTable, gridOptions);
    refreshCertificateGridRows();
    return state.certificateExtraction.gridApi;
}

function refreshCertificateGridRows() {
    const gridApi = ensureCertificateGridApi();
    if (!gridApi) {
        return;
    }

    const rowData = buildCertificateGridRowData();
    gridApi.setGridOption('rowData', rowData);
    if (rowData.length === 0) {
        gridApi.showNoRowsOverlay();
    } else {
        gridApi.hideOverlay();
    }
}

function bindCertificateInteractionHandlers() {
    elements.certFilesList.addEventListener('change', (event) => {
        const target = event.target;
        if (!(target instanceof HTMLInputElement)) {
            return;
        }
        const filePath = target.dataset.certFilePath;
        if (!filePath) {
            return;
        }
        toggleCertificateFile(filePath, target.checked);
    });
}

function bindSharedResultInteractionHandlers() {
    document.addEventListener('click', (event) => {
        const actionElement = event.target.closest('[data-action]');
        if (!actionElement) {
            return;
        }

        const action = actionElement.dataset.action;
        if (!action) {
            return;
        }

        switch (action) {
            case 'remove-file':
                removeFile(actionElement.dataset.tool, actionElement.dataset.filePath);
                break;
            case 'open-file':
                event.preventDefault();
                openFile(actionElement.dataset.filePath);
                break;
            case 'open-folder':
                openFolder(actionElement.dataset.folderPath);
                break;
            case 'download-file':
                downloadFile(actionElement.dataset.filename, actionElement.dataset.fileContent);
                break;
            case 'toggle-collapsible':
                toggleCollapsible(actionElement.dataset.blockId);
                break;
            case 'keep-only-16h':
                keepOnly16hFiles();
                break;
            case 'keep-only-32h':
                keepOnly32hFiles();
                break;
            case 'clear-all-zor':
                clearAllZorFiles();
                break;
            default:
                break;
        }
    });

    document.addEventListener('change', (event) => {
        const target = event.target;
        if (!(target instanceof HTMLInputElement)) {
            return;
        }

        if (target.dataset.action === 'toggle-dvpp-file' && target.dataset.filePath) {
            toggleDvppFile(target.dataset.filePath, target.checked);
        }
    });
}

function renderCertificateDiagnostics() {
    if (!state.certificateExtraction.diagnostics.length) {
        elements.certDiagnostics.className = 'cert-diagnostics empty-state';
        elements.certDiagnostics.textContent = 'Diagnostika se zobrazí po importu.';
        return;
    }

    elements.certDiagnostics.className = 'cert-diagnostics';
    elements.certDiagnostics.innerHTML = `
        <ul class="cert-diagnostics-list">
            ${state.certificateExtraction.diagnostics.map((item) => `
                <li class="cert-diagnostic-item ${item.success ? 'success' : 'error'}">
                    <strong>${escapeHtml(wslToWindowsPath(item.source_file || 'text'))}</strong><br>
                    ${item.success ? `Vytěženo záznamů: ${item.record_count}` : escapeHtml((item.errors || []).join(', '))}
                </li>
            `).join('')}
        </ul>
    `;
}

function updateCertificateField(index, field, value) {
    const record = state.certificateExtraction.records[index];
    if (!record) {
        return;
    }
    record.working_record[field] = value;
}

function removeCertificateRecord(index) {
    state.certificateExtraction.records.splice(index, 1);
    refreshCertificateGridRows();
    updateCertificateActions();
}

function applyCertificateTemplateToAllRecords() {
    const selectedTemplate = elements.certBulkTemplateSelect.value;
    if (!selectedTemplate) {
        showMessage('Nejprve vyberte šablonu pro hromadné vyplnění.', 'warning');
        return;
    }

    if (!state.certificateExtraction.records.length) {
        showMessage('Zatím nejsou načtené žádné certifikáty.', 'warning');
        return;
    }

    state.certificateExtraction.records.forEach((record) => {
        record.working_record.sablona = selectedTemplate;
    });

    refreshCertificateGridRows();
    showMessage(`Šablona ${selectedTemplate} byla nastavena do všech řádků.`, 'success');
}

function applyCertificateFormaToAllRecords() {
    const selectedForma = elements.certBulkFormaSelect.value;
    if (!selectedForma) {
        showMessage('Nejprve vyberte formu DVPP pro hromadné vyplnění.', 'warning');
        return;
    }

    if (!state.certificateExtraction.records.length) {
        showMessage('Zatím nejsou načtené žádné certifikáty.', 'warning');
        return;
    }

    state.certificateExtraction.records.forEach((record) => {
        record.working_record.forma = selectedForma;
    });

    refreshCertificateGridRows();
    showMessage(`Forma ${selectedForma} byla nastavena do všech řádků.`, 'success');
}

function applyCertificatePohlaviToAllRecords() {
    const selectedPohlavi = elements.certBulkPohlaviSelect.value;
    if (!selectedPohlavi) {
        showMessage('Nejprve vyberte pohlaví pro hromadné vyplnění.', 'warning');
        return;
    }

    if (!state.certificateExtraction.records.length) {
        showMessage('Zatím nejsou načtené žádné certifikáty.', 'warning');
        return;
    }

    state.certificateExtraction.records.forEach((record) => {
        record.working_record.pohlavi = selectedPohlavi;
    });

    refreshCertificateGridRows();
    showMessage(`Pohlaví ${selectedPohlavi} bylo nastaveno do všech řádků.`, 'success');
}

function updateCertificateActions() {
    const hasSelectedFiles = state.selectedFiles['dvpp-certificates'].length > 0;
    elements.certProcessGeminiBtn.disabled = !state.certificateExtraction.folderPath || !hasSelectedFiles;
    const hasRecords = state.certificateExtraction.records.length > 0;
    elements.certCopyTsvBtn.disabled = !hasRecords;
    elements.certSaveTsvBtn.disabled = !hasRecords;
    elements.certSaveExcelBtn.disabled = !hasRecords;
    elements.certSaveEsfBtn.disabled = !hasRecords;
    elements.certApplyTemplateAllBtn.disabled = !hasRecords;
    elements.certApplyFormaAllBtn.disabled = !hasRecords;
    elements.certApplyPohlaviAllBtn.disabled = !hasRecords;
}

async function copyCertificateTsv() {
    try {
        const result = await window.electronAPI.apiCall('dvpp-certificates/export/tsv', 'POST', {
            records: state.certificateExtraction.records
        });
        await copyTextToClipboard(result.data.content, 'TSV obsah byl zkopírován do schránky.');
    } catch (error) {
        console.error('Copy TSV error:', error);
        showMessage(`Chyba při kopírování TSV: ${error.message}`, 'error');
    }
}

async function saveCertificateTsv() {
    try {
        const outputPath = await window.electronAPI.saveFile('dvpp_certificates.tsv');
        if (!outputPath) {
            return;
        }

        await window.electronAPI.apiCall('dvpp-certificates/export/tsv', 'POST', {
            records: state.certificateExtraction.records,
            outputPath
        });
        showMessage(`TSV export byl uložen: ${wslToWindowsPath(outputPath)}`, 'success');
    } catch (error) {
        console.error('Save TSV error:', error);
        showMessage(`Chyba při ukládání TSV: ${error.message}`, 'error');
    }
}

async function saveCertificateExcel() {
    try {
        const outputPath = await window.electronAPI.saveFile('dvpp_certificates.xlsx');
        if (!outputPath) {
            return;
        }

        const result = await window.electronAPI.apiCall('dvpp-certificates/export/excel', 'POST', {
            records: state.certificateExtraction.records,
            exportMetadata: state.certificateExtraction.exportMetadata,
            templatePath: state.certificateExtraction.exportMetadata.template_path,
            outputPath
        });
        showMessage(`Excel export byl vytvořen: ${wslToWindowsPath(result.data.output_path)}`, 'success');
        await openFile(result.data.output_path);
    } catch (error) {
        console.error('Save Excel error:', error);
        showMessage(`Chyba při vytváření Excelu: ${error.message}`, 'error');
    }
}

async function saveCertificateEsfImport() {
    try {
        const outputPath = await window.electronAPI.saveFile('osoby.csv');
        if (!outputPath) {
            return;
        }

        const result = await window.electronAPI.apiCall('dvpp-certificates/export/esf', 'POST', {
            records: state.certificateExtraction.records,
            exportMetadata: state.certificateExtraction.exportMetadata,
            outputPath
        });
        showMessage(`ESF import byl vytvořen: ${wslToWindowsPath(result.data.output_path)}`, 'success');
        await openFile(result.data.output_path);
    } catch (error) {
        console.error('Save ESF import error:', error);
        showMessage(`Chyba při vytváření ESF importu: ${error.message}`, 'error');
    }
}

async function selectCertificateTemplate() {
    try {
        const filePaths = await window.electronAPI.openFile({
            multiple: false,
            filters: [{ name: 'Excel Files', extensions: ['xlsx', 'xlsm', 'xltx', 'xltm'] }]
        });
        if (!filePaths || filePaths.length === 0) {
            return;
        }
        state.certificateExtraction.exportMetadata.template_path = filePaths[0];
        elements.certTemplatePath.value = filePaths[0];
    } catch (error) {
        console.error('Select certificate template error:', error);
        showMessage('Chyba při výběru Excel šablony.', 'error');
    }
}

async function copyTextToClipboard(text, successMessage) {
    try {
        await navigator.clipboard.writeText(text);
        if (successMessage) {
            showMessage(successMessage, 'success');
            setStatusMessage(successMessage, 4000);
        }
    } catch (error) {
        console.error('Clipboard error:', error);
        showMessage('Nepodařilo se zkopírovat text do schránky.', 'error');
    }
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Detect mixed versions in file list
function detectMixedVersions(filePaths) {
    let has16h = false;
    let has32h = false;
    const files16h = [];
    const files32h = [];

    filePaths.forEach(filePath => {
        const filename = filePath.split(/[/\\]/).pop().toLowerCase();
        // Check for 32h indicators
        if (filename.includes('32h_') || filename.includes('32_inv') ||
            filename.includes('32_hodin') || filename.includes('32h')) {
            has32h = true;
            files32h.push(filePath.split(/[/\\]/).pop());
        } else {
            has16h = true;
            files16h.push(filePath.split(/[/\\]/).pop());
        }
    });

    return {
        mixed: has16h && has32h,
        has16h,
        has32h,
        files16h,
        files32h,
        count16h: files16h.length,
        count32h: files32h.length
    };
}

// Show error message for mixed versions
function showZorVersionError(versionCheck) {
    // Remove existing error if any
    const existingError = document.getElementById('zor-version-error');
    if (existingError) existingError.remove();

    // Create error message element
    const errorDiv = document.createElement('div');
    errorDiv.id = 'zor-version-error';
    errorDiv.className = 'version-error-panel';
    errorDiv.innerHTML = `
        <div class="version-error-header">
            <div class="version-error-icon">⚠️</div>
            <div class="version-error-title">
                <h4>Nelze kombinovat různé verze šablon</h4>
                <p>Zpracování je zablokováno z důvodu smíšených verzí</p>
            </div>
        </div>
        <div class="version-error-body">
            <div class="version-error-details">
                <div class="version-detail">
                    <span class="version-badge version-16h">16h</span>
                    <span class="version-count">${versionCheck.count16h} souborů Šablony I</span>
                </div>
                <div class="version-detail">
                    <span class="version-badge version-32h">32h</span>
                    <span class="version-count">${versionCheck.count32h} souborů Šablony II</span>
                </div>
            </div>
            <div class="version-error-solution">
                <p><strong>Jak to vyřešit:</strong></p>
                <p>Odeberte všechny soubory jedné verze ze seznamu níže, nebo:</p>
                <div class="version-error-actions">
                    <button class="btn-action btn-keep-16h" type="button" data-action="keep-only-16h">
                        <span class="btn-icon">📋</span>
                        Ponechat pouze 16h verzi
                    </button>
                    <button class="btn-action btn-keep-32h" type="button" data-action="keep-only-32h">
                        <span class="btn-icon">📋</span>
                        Ponechat pouze 32h verzi
                    </button>
                    <button class="btn-action btn-clear-all" type="button" data-action="clear-all-zor">
                        <span class="btn-icon">🗑️</span>
                        Smazat vše a začít znovu
                    </button>
                </div>
            </div>
        </div>
    `;

    // Insert before the file list
    const fileListContainer = elements.zorFilesList.parentElement;
    fileListContainer.insertBefore(errorDiv, elements.zorFilesList);
}

// Keep only 16h files
function keepOnly16hFiles() {
    const versionCheck = detectMixedVersions(state.selectedFiles['zor-spec']);
    state.selectedFiles['zor-spec'] = state.selectedFiles['zor-spec'].filter(filePath => {
        const filename = filePath.split(/[/\\]/).pop().toLowerCase();
        return !(filename.includes('32h_') || filename.includes('32_inv') ||
                 filename.includes('32_hodin') || filename.includes('32h'));
    });
    updateFilesList('zor-spec');
    checkZorSpecReady();
}

// Keep only 32h files
function keepOnly32hFiles() {
    const versionCheck = detectMixedVersions(state.selectedFiles['zor-spec']);
    state.selectedFiles['zor-spec'] = state.selectedFiles['zor-spec'].filter(filePath => {
        const filename = filePath.split(/[/\\]/).pop().toLowerCase();
        return (filename.includes('32h_') || filename.includes('32_inv') ||
                filename.includes('32_hodin') || filename.includes('32h'));
    });
    updateFilesList('zor-spec');
    checkZorSpecReady();
}

// Clear all ZorSpec files
function clearAllZorFiles() {
    state.selectedFiles['zor-spec'] = [];
    state.zorFileVersions = {};
    updateFilesList('zor-spec');
    checkZorSpecReady();
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

        // Track processing time
        const startTime = performance.now();

        // Use path-based processing with auto-save
        const result = await window.electronAPI.apiCall('process/zor-spec-paths', 'POST', {
            filePaths: state.selectedFiles['zor-spec'],
            options: {},
            autoSave: true  // Auto-save to source folder
        });

        // Calculate duration
        const duration = ((performance.now() - startTime) / 1000).toFixed(1);

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
                    <span class="status-time">Doba trvání: ${duration}s</span>
                </div>
            `;

            // Show warnings right after status banner
            if (result.warnings && result.warnings.length > 0) {
                resultHtml += `
                    <div class="warning-banner">
                        <div class="warning-banner-icon">⚠️</div>
                        <div class="warning-banner-content">
                            <h4>Varování při zpracování</h4>
                            <ul class="warning-banner-list">
                `;
                result.warnings.forEach(msg => {
                    resultHtml += `<li>${msg}</li>`;
                });
                resultHtml += `
                            </ul>
                        </div>
                    </div>
                `;
            }

            resultHtml += `
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
                const hourThreshold = students16.hour_threshold || 16;  // Default to 16 if not provided
                resultHtml += `
                    <div class="section-header">Počet dětí/žáků se splněnou docházkou ${hourThreshold}h</div>
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

                        <div class="stat-card school-card">
                            <div class="stat-content">
                                <div class="stat-label">ZÁKLADNÍ UMĚLECKÁ ŠKOLA</div>
                                <div class="stat-value">${students16['ZUŠ'] || 0}</div>
                            </div>
                            <div class="stat-icon school-icon">🎨</div>
                        </div>

                        <div class="stat-card school-card">
                            <div class="stat-content">
                                <div class="stat-label">STŘEDNÍ ŠKOLA</div>
                                <div class="stat-value">${students16['SŠ'] || 0}</div>
                            </div>
                            <div class="stat-icon school-icon">🎓</div>
                        </div>
                    </div>
                `;
            }

            // Control sums - total hours for forms and topics
            if (result.data.students_16plus &&
                (result.data.students_16plus.total_forma_hours !== undefined ||
                 result.data.students_16plus.total_tema_hours !== undefined)) {
                const students16 = result.data.students_16plus;
                resultHtml += `
                    <div class="section-header">Kontrolní součty hodin</div>
                    <div class="stats-grid control-sums">
                        <div class="stat-card">
                            <div class="stat-content">
                                <div class="stat-label">CELKEM HODIN - FORMY</div>
                                <div class="stat-value">${students16.total_forma_hours || 0}</div>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-content">
                                <div class="stat-label">CELKEM HODIN - TÉMATA</div>
                                <div class="stat-value">${students16.total_tema_hours || 0}</div>
                            </div>
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
                                    <button class="copy-btn" type="button" data-action="open-folder" data-folder-path="${escapeHtml(displayPath)}" title="Otevřít složku s výsledky">
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
                                    <button class="file-btn btn-view" type="button" data-action="open-file" data-file-path="${escapeHtml(fullPath)}">
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
                                <button class="btn btn-small" type="button" data-action="download-file" data-filename="${escapeHtml(file.filename)}" data-file-content="${escapeHtml(file.content)}">
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
                            
                            resultHtml += `<li>${description}: <a href="#" class="file-link" data-action="open-file" data-file-path="${escapeHtml(fullPath)}">${filename}</a></li>`;
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
            <div class="file-header collapsible-header" data-action="toggle-collapsible" data-block-id="${escapeHtml(blockId)}">
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
