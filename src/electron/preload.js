const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // File dialogs
    openFile: () => ipcRenderer.invoke('dialog:openFile'),
    saveFile: (defaultName) => ipcRenderer.invoke('dialog:saveFile', defaultName),
    
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
    uploadFiles: async (endpoint, files, options = {}) => {
        const formData = new FormData();
        
        // Add files to form data
        for (const file of files) {
            formData.append('files', file);
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
    }
});