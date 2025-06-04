const { contextBridge, ipcRenderer } = require('electron');

// Backend recovery event listener
ipcRenderer.on('backend-failed', (event, data) => {
    window.dispatchEvent(new CustomEvent('backend-failed', { detail: data }));
});

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // File dialogs
    openFile: (options) => ipcRenderer.invoke('dialog:openFile', options),
    saveFile: (defaultName) => ipcRenderer.invoke('dialog:saveFile', defaultName),
    selectFolder: (options) => ipcRenderer.invoke('dialog:selectFolder', options),
    writeFile: (path, data) => ipcRenderer.invoke('file:write', path, data),
    openFileInApp: (filePath) => ipcRenderer.invoke('file:openInApp', filePath),
    
    // Config
    getConfig: (key) => ipcRenderer.invoke('config:get', key),
    setConfig: (key, value) => ipcRenderer.invoke('config:set', key, value),
    
    // File system operations
    scanFolder: (folderPath) => ipcRenderer.invoke('fs:scanFolder', folderPath),
    
    // API calls to Python backend
    apiCall: async (endpoint, method = 'GET', data = null) => {
        const baseURL = 'http://localhost:5000/api';
        const url = `${baseURL}/${endpoint}`;
        
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data && method !== 'GET') {
            if (data instanceof FormData) {
                delete options.headers['Content-Type'];
                options.body = data;
            } else {
                options.body = JSON.stringify(data);
            }
        }
        
        try {
            const response = await fetch(url, options);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.message || 'API request failed');
            }
            
            return result;
        } catch (error) {
            console.error('API call error:', error);
            throw error;
        }
    },
    
    // File operations
    uploadFiles: async (endpoint, files, template = null, options = {}) => {
        const formData = new FormData();
        
        // Add files to form data
        for (const file of files) {
            formData.append('files', file);
        }
        
        // Add template if provided
        if (template) {
            formData.append('template', template);
        }
        
        // Add options if provided
        if (Object.keys(options).length > 0) {
            formData.append('options', JSON.stringify(options));
        }
        
        const baseURL = 'http://localhost:5000/api';
        const url = `${baseURL}/${endpoint}`;
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.message || 'Upload failed');
            }
            
            return result;
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    },
    
    // Upload form data directly
    uploadFormData: async (endpoint, formData) => {
        const baseURL = 'http://localhost:5000/api';
        const url = `${baseURL}/${endpoint}`;
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.message || 'Upload failed');
            }
            
            return result;
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    },
    
    // Backend management
    getBackendStatus: () => ipcRenderer.invoke('backend:getStatus'),
    restartBackend: () => ipcRenderer.invoke('backend:restart'),
    
    // Listen for backend failures
    onBackendFailed: (callback) => {
        window.addEventListener('backend-failed', (event) => {
            callback(event.detail);
        });
    },
    
    // App info
    getVersion: () => ipcRenderer.invoke('app:getVersion')
});