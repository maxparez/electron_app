const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const axios = require('axios');
const config = require('./config');

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
    app.quit();
}

let mainWindow;
let pythonProcess;
const isDev = process.argv.includes('--dev');

// Create the main application window
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        icon: path.join(__dirname, 'assets', 'icon.png'),
        autoHideMenuBar: true, // Hide menu bar in production
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    // Load the index.html file
    mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));

    // Open DevTools in development mode
    if (isDev) {
        mainWindow.webContents.openDevTools();
    }

    // Handle window closed
    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}

// Start the Python backend server
function startPythonServer() {
    const script = path.join(__dirname, '..', 'python', 'server.py');
    
    // Use the virtual environment Python if it exists
    const venvPython = path.join(process.cwd(), 'venv', 'bin', 'python');
    const pythonCommand = require('fs').existsSync(venvPython) ? venvPython : 'python3';
    
    console.log('Starting Python server:', pythonCommand, script);
    
    pythonProcess = spawn(pythonCommand, [script], {
        cwd: process.cwd(),
        env: { ...process.env, PYTHONUNBUFFERED: '1' }
    });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python stdout: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Python stderr: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
        pythonProcess = null;
    });

    // Wait for server to start
    return waitForServer();
}

// Wait for the Python server to be ready
async function waitForServer(retries = 30) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await axios.get('http://localhost:5000/api/health');
            if (response.data.status === 'healthy') {
                console.log('Python server is ready');
                return true;
            }
        } catch (error) {
            // Server not ready yet
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    throw new Error('Python server failed to start');
}

// Stop the Python server
function stopPythonServer() {
    if (pythonProcess) {
        console.log('Stopping Python server...');
        pythonProcess.kill();
        pythonProcess = null;
    }
}

// IPC handlers for communication with renderer
ipcMain.handle('dialog:openFile', async (event, options = {}) => {
    const defaultOptions = {
        properties: ['openFile'],
        filters: [
            { name: 'Excel Files', extensions: ['xlsx', 'xls'] },
            { name: 'All Files', extensions: ['*'] }
        ]
    };
    
    // Merge with provided options
    const dialogOptions = { ...defaultOptions, ...options };
    
    // Add multiSelections if needed
    if (options.multiple) {
        dialogOptions.properties.push('multiSelections');
    }
    
    const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, dialogOptions);
    
    if (!canceled) {
        return filePaths;
    }
    return [];
});

ipcMain.handle('dialog:saveFile', async (event, defaultName) => {
    const { canceled, filePath } = await dialog.showSaveDialog(mainWindow, {
        defaultPath: defaultName,
        filters: [
            { name: 'PDF Files', extensions: ['pdf'] },
            { name: 'Excel Files', extensions: ['xlsx'] },
            { name: 'All Files', extensions: ['*'] }
        ]
    });
    
    if (!canceled) {
        return filePath;
    }
    return null;
});

ipcMain.handle('file:write', async (event, filePath, data) => {
    const fs = require('fs').promises;
    try {
        // Convert Uint8Array to Buffer
        const buffer = Buffer.from(data);
        await fs.writeFile(filePath, buffer);
        return { success: true };
    } catch (error) {
        console.error('File write error:', error);
        throw error;
    }
});

ipcMain.handle('dialog:selectFolder', async (event, options = {}) => {
    const defaultOptions = {
        properties: ['openDirectory'],
        title: 'Vyberte složku pro uložení',
        buttonLabel: 'Vybrat složku'
    };
    
    // Use last selected folder as default
    const lastFolder = config.get(options.configKey || 'lastFolder');
    if (lastFolder) {
        defaultOptions.defaultPath = lastFolder;
    }
    
    const dialogOptions = { ...defaultOptions, ...options };
    
    const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, dialogOptions);
    
    if (!canceled && filePaths.length > 0) {
        const selectedPath = filePaths[0];
        // Save to config if configKey provided
        if (options.configKey) {
            config.set(options.configKey, selectedPath);
        }
        return selectedPath;
    }
    return null;
});

ipcMain.handle('config:get', (event, key) => {
    return config.get(key);
});

ipcMain.handle('config:set', (event, key, value) => {
    config.set(key, value);
    return true;
});

ipcMain.handle('fs:scanFolder', async (event, folderPath) => {
    const fs = require('fs').promises;
    const path = require('path');
    
    try {
        const files = await fs.readdir(folderPath);
        const fileStats = await Promise.all(
            files.map(async (file) => {
                const filePath = path.join(folderPath, file);
                const stat = await fs.stat(filePath);
                return {
                    name: file,
                    path: filePath,
                    isFile: stat.isFile(),
                    isDirectory: stat.isDirectory(),
                    size: stat.size,
                    mtime: stat.mtime
                };
            })
        );
        
        return {
            files: fileStats.filter(f => f.isFile).map(f => f.name),
            directories: fileStats.filter(f => f.isDirectory).map(f => f.name)
        };
    } catch (error) {
        console.error('Error scanning folder:', error);
        throw error;
    }
});

// Open file in associated application
ipcMain.handle('file:openInApp', async (event, filePath) => {
    const fs = require('fs');
    
    try {
        // Check if file exists
        if (!fs.existsSync(filePath)) {
            return {
                success: false,
                error: 'Soubor neexistuje'
            };
        }
        
        // Open file with default application
        await shell.openPath(filePath);
        
        return {
            success: true,
            filename: require('path').basename(filePath)
        };
    } catch (error) {
        console.error('Error opening file:', error);
        return {
            success: false,
            error: error.message || 'Neznámá chyba'
        };
    }
});

// App event handlers
app.whenReady().then(async () => {
    try {
        // Start Python server first
        await startPythonServer();
        
        // Then create the window
        createWindow();
    } catch (error) {
        console.error('Failed to start application:', error);
        dialog.showErrorBox('Chyba spuštění', 'Nepodařilo se spustit Python server');
        app.quit();
    }
});

app.on('window-all-closed', () => {
    // On macOS, keep app running even when all windows are closed
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    // On macOS, re-create window when dock icon is clicked
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

app.on('will-quit', () => {
    // Clean up Python process
    stopPythonServer();
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error('Uncaught exception:', error);
    dialog.showErrorBox('Neočekávaná chyba', error.message);
});