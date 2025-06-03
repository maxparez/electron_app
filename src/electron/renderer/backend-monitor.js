// Backend monitoring and recovery UI

let backendFailureCount = 0;
let isBackendHealthy = true;

// Listen for backend failures
window.electronAPI.onBackendFailed((data) => {
    console.error('Backend failed:', data);
    backendFailureCount++;
    isBackendHealthy = false;
    
    showBackendError(data);
});

function showBackendError(data) {
    // Create error modal
    const modal = document.createElement('div');
    modal.className = 'backend-error-modal';
    modal.innerHTML = `
        <div class="modal-overlay">
            <div class="modal-content error-modal">
                <h2>⚠️ Chyba Python backendu</h2>
                <p class="error-message">${data.message}</p>
                
                <div class="error-details">
                    <h3>Detaily:</h3>
                    <p>Backend selhal ${backendFailureCount}x</p>
                    <p>Poslední pád: ${new Date().toLocaleString('cs-CZ')}</p>
                </div>
                
                <div class="error-actions">
                    <button class="btn btn-primary" onclick="restartBackend()">
                        🔄 Restartovat backend
                    </button>
                    <button class="btn btn-secondary" onclick="viewCrashLog()">
                        📋 Zobrazit crash log
                    </button>
                    <button class="btn btn-secondary" onclick="closeErrorModal()">
                        ❌ Zavřít
                    </button>
                </div>
                
                <div class="error-help">
                    <p><strong>Možné příčiny:</strong></p>
                    <ul>
                        <li>Port 5000 je obsazený jiným programem</li>
                        <li>Chybí Python nebo potřebné knihovny</li>
                        <li>Nedostatečná oprávnění</li>
                        <li>Chyba v konfiguraci</li>
                    </ul>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

async function restartBackend() {
    try {
        closeErrorModal();
        showLoading('Restartuji Python backend...');
        
        const result = await window.electronAPI.restartBackend();
        
        if (result) {
            isBackendHealthy = true;
            backendFailureCount = 0;
            hideLoading();
            showSuccess('Backend byl úspěšně restartován');
        } else {
            hideLoading();
            showError('Nepodařilo se restartovat backend');
        }
    } catch (error) {
        hideLoading();
        showError('Chyba při restartu: ' + error.message);
    }
}

async function viewCrashLog() {
    try {
        const status = await window.electronAPI.getBackendStatus();
        
        if (status.crashLog && status.crashLog.length > 0) {
            const logModal = document.createElement('div');
            logModal.className = 'crash-log-modal';
            logModal.innerHTML = `
                <div class="modal-overlay">
                    <div class="modal-content log-modal">
                        <h2>📋 Crash Log</h2>
                        <div class="log-content">
                            <pre>${JSON.stringify(status.crashLog, null, 2)}</pre>
                        </div>
                        <div class="modal-actions">
                            <button class="btn btn-primary" onclick="copyCrashLog()">
                                📋 Kopírovat
                            </button>
                            <button class="btn btn-secondary" onclick="closeCrashLogModal()">
                                ❌ Zavřít
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(logModal);
        } else {
            showInfo('Žádný crash log není k dispozici');
        }
    } catch (error) {
        showError('Nepodařilo se načíst crash log');
    }
}

function copyCrashLog() {
    const logContent = document.querySelector('.log-content pre').textContent;
    navigator.clipboard.writeText(logContent).then(() => {
        showSuccess('Log byl zkopírován do schránky');
    });
}

function closeErrorModal() {
    const modal = document.querySelector('.backend-error-modal');
    if (modal) {
        modal.remove();
    }
}

function closeCrashLogModal() {
    const modal = document.querySelector('.crash-log-modal');
    if (modal) {
        modal.remove();
    }
}

// Health check
async function checkBackendHealth() {
    if (!isBackendHealthy) return;
    
    try {
        const response = await fetch('http://localhost:5000/api/health');
        if (!response.ok) {
            throw new Error('Backend not responding');
        }
        
        const data = await response.json();
        if (data.status !== 'healthy') {
            throw new Error('Backend unhealthy');
        }
        
        // Update UI indicator if exists
        const indicator = document.querySelector('.backend-status');
        if (indicator) {
            indicator.classList.add('healthy');
            indicator.classList.remove('unhealthy');
            indicator.title = 'Backend běží správně';
        }
    } catch (error) {
        // Update UI indicator if exists
        const indicator = document.querySelector('.backend-status');
        if (indicator) {
            indicator.classList.add('unhealthy');
            indicator.classList.remove('healthy');
            indicator.title = 'Backend neodpovídá';
        }
    }
}

// Check backend health every 30 seconds
setInterval(checkBackendHealth, 30000);

// Initial check
setTimeout(checkBackendHealth, 2000);

// Add CSS for modals
const style = document.createElement('style');
style.textContent = `
.backend-error-modal .modal-overlay,
.crash-log-modal .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
}

.modal-content {
    background: white;
    border-radius: 12px;
    padding: 30px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.error-modal h2 {
    color: #dc3545;
    margin-bottom: 20px;
}

.error-message {
    font-size: 16px;
    color: #666;
    margin-bottom: 20px;
}

.error-details {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.error-actions {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.error-help {
    background: #fff3cd;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #ffc107;
}

.error-help ul {
    margin: 10px 0 0 20px;
}

.log-modal .log-content {
    background: #f5f5f5;
    padding: 15px;
    border-radius: 8px;
    margin: 20px 0;
    max-height: 400px;
    overflow-y: auto;
}

.log-modal pre {
    margin: 0;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    white-space: pre-wrap;
}

.modal-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
}

.backend-status {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
    margin-left: 10px;
}

.backend-status.healthy {
    background-color: #28a745;
}

.backend-status.unhealthy {
    background-color: #dc3545;
}
`;
document.head.appendChild(style);