const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const { app } = require('electron');

class BackendManager {
    constructor() {
        this.pythonProcess = null;
        this.isShuttingDown = false;
        this.restartAttempts = 0;
        this.lastStartTime = null;
        this.crashLog = [];
        
        // Load config
        const config = require('./config');
        this.maxRestartAttempts = config.get('backend.maxRestartAttempts', 5);
        this.restartDelay = config.get('backend.restartDelay', 3000);
    }

    async start() {
        console.log('[BackendManager] Starting Python backend...');
        this.lastStartTime = Date.now();
        
        try {
            const isProd = !process.argv.includes('--dev');
            const appPath = isProd ? process.resourcesPath : app.getAppPath();
            
            // Determine Python executable path
            let pythonPath;
            if (isProd) {
                // In production, first try the electron-app-env created by our installer
                const appDir = path.dirname(process.execPath);
                const userInstallVenv = path.join(appDir, 'electron-app-env', 'Scripts', 'python.exe');
                
                // Also try parent directory (where user might have installed)
                const parentVenv = path.join(appDir, '..', 'electron-app-env', 'Scripts', 'python.exe');
                
                // Check environment variable set by launcher
                const envPythonPath = process.env.ELECTRON_APP_PYTHON_ENV ? 
                    path.join(process.env.ELECTRON_APP_PYTHON_ENV, 'Scripts', 'python.exe') : null;
                
                // Check common installation locations relative to exe
                const exeDir = path.dirname(process.execPath);
                const twoLevelsUp = path.join(exeDir, '..', '..', 'electron-app-env', 'Scripts', 'python.exe');
                const threeLevelsUp = path.join(exeDir, '..', '..', '..', 'electron-app-env', 'Scripts', 'python.exe');
                
                // Original bundled locations (if we had bundled Python)
                const possiblePaths = [
                    envPythonPath,    // NEW: From environment variable
                    userInstallVenv,  // NEW: From our install script
                    parentVenv,       // NEW: Parent directory
                    twoLevelsUp,      // NEW: Common installation location
                    threeLevelsUp,    // NEW: Alternative installation location
                    path.join(process.resourcesPath, 'python', 'python.exe'),
                    path.join(process.resourcesPath, 'python-dist', 'python', 'python.exe'),
                    path.join(process.resourcesPath, 'app.asar.unpacked', 'python-dist', 'python', 'python.exe'),
                    path.join(process.resourcesPath, '..', 'python', 'python.exe')
                ].filter(p => p); // Remove null entries
                
                pythonPath = possiblePaths.find(p => fs.existsSync(p));
                
                if (!pythonPath) {
                    // Log all tried paths for debugging
                    console.error('[BackendManager] Python not found. Tried paths:');
                    possiblePaths.forEach(p => console.error(`  - ${p}`));
                    
                    // Fallback to system Python
                    console.warn('[BackendManager] Falling back to system Python');
                    pythonPath = 'python';
                }
            } else {
                // In development, use venv if exists, otherwise system Python
                const venvPython = path.join(app.getAppPath(), 'venv', 'Scripts', 'python.exe');
                if (fs.existsSync(venvPython)) {
                    pythonPath = venvPython;
                } else {
                    pythonPath = 'python';
                }
            }
            
            // Determine script path - check multiple possible locations
            let scriptPath;
            if (isProd) {
                const possibleScriptPaths = [
                    path.join(process.resourcesPath, 'python', 'server.py'),
                    path.join(process.resourcesPath, 'app.asar.unpacked', 'src', 'python', 'server.py'),
                    path.join(process.resourcesPath, 'app.asar.unpacked', 'python', 'server.py'),
                    path.join(appPath, 'resources', 'python', 'server.py')
                ];
                
                scriptPath = possibleScriptPaths.find(p => fs.existsSync(p));
                
                if (!scriptPath) {
                    console.error('[BackendManager] Script not found. Tried paths:');
                    possibleScriptPaths.forEach(p => console.error(`  - ${p}`));
                    throw new Error('Python script server.py not found');
                }
            } else {
                scriptPath = path.join(appPath, 'src', 'python', 'server.py');
            }
            
            console.log('[BackendManager] Python path:', pythonPath);
            console.log('[BackendManager] Script path:', scriptPath);
            
            // Set environment variables
            const config = require('./config');
            const env = {
                ...process.env,
                PYTHONUNBUFFERED: '1',
                FLASK_DEBUG: config.get('python.debug', !isProd) ? 'true' : 'false',
                PYTHONPATH: isProd 
                    ? path.join(process.resourcesPath, 'app.asar.unpacked', 'src', 'python')
                    : path.join(appPath, 'src', 'python'),
                FLASK_PORT: config.get('python.port', 5000)
            };
            
            this.pythonProcess = spawn(pythonPath, [scriptPath], {
                cwd: appPath,
                env: env
            });
            
            this.pythonProcess.stdout.on('data', (data) => {
                console.log(`[Python] ${data.toString().trim()}`);
            });
            
            this.pythonProcess.stderr.on('data', (data) => {
                const message = data.toString().trim();
                console.error(`[Python ERROR] ${message}`);
                this.crashLog.push({
                    time: new Date().toISOString(),
                    type: 'stderr',
                    message: message
                });
            });
            
            this.pythonProcess.on('error', (error) => {
                console.error('[BackendManager] Process error:', error);
                this.crashLog.push({
                    time: new Date().toISOString(),
                    type: 'error',
                    message: error.message
                });
            });
            
            this.pythonProcess.on('exit', (code, signal) => {
                console.log(`[BackendManager] Python process exited with code ${code}, signal ${signal}`);
                this.pythonProcess = null;
                
                if (!this.isShuttingDown) {
                    this.handleCrash(code, signal);
                }
            });
            
            // Reset restart attempts on successful start
            setTimeout(() => {
                if (this.pythonProcess) {
                    this.restartAttempts = 0;
                    console.log('[BackendManager] Backend started successfully');
                }
            }, 5000);
            
            return true;
        } catch (error) {
            console.error('[BackendManager] Failed to start backend:', error);
            this.crashLog.push({
                time: new Date().toISOString(),
                type: 'start_error',
                message: error.message
            });
            return false;
        }
    }
    
    async handleCrash(exitCode, signal) {
        const runtime = Date.now() - this.lastStartTime;
        console.log(`[BackendManager] Crash detected. Runtime: ${runtime}ms`);
        
        this.crashLog.push({
            time: new Date().toISOString(),
            type: 'crash',
            exitCode: exitCode,
            signal: signal,
            runtime: runtime,
            attempt: this.restartAttempts + 1
        });
        
        // If crashed too quickly, increase delay
        if (runtime < 10000) { // Less than 10 seconds
            this.restartDelay = Math.min(this.restartDelay * 2, 60000); // Max 1 minute
        } else {
            this.restartDelay = 3000; // Reset to 3 seconds
        }
        
        if (this.restartAttempts < this.maxRestartAttempts) {
            this.restartAttempts++;
            console.log(`[BackendManager] Attempting restart ${this.restartAttempts}/${this.maxRestartAttempts} in ${this.restartDelay}ms...`);
            
            setTimeout(() => {
                this.start();
            }, this.restartDelay);
        } else {
            console.error('[BackendManager] Max restart attempts reached. Backend will not restart automatically.');
            this.saveCrashLog();
            
            // Notify main window about the failure
            const { BrowserWindow } = require('electron');
            const mainWindow = BrowserWindow.getAllWindows()[0];
            if (mainWindow) {
                mainWindow.webContents.send('backend-failed', {
                    message: 'Python backend selhalo opakovaně',
                    crashLog: this.crashLog
                });
            }
        }
    }
    
    stop() {
        this.isShuttingDown = true;
        
        if (this.pythonProcess) {
            console.log('[BackendManager] Stopping Python backend...');
            
            // Try graceful shutdown first
            this.pythonProcess.kill('SIGTERM');
            
            // Force kill after 5 seconds if still running
            setTimeout(() => {
                if (this.pythonProcess) {
                    console.log('[BackendManager] Force killing Python process...');
                    this.pythonProcess.kill('SIGKILL');
                }
            }, 5000);
        }
    }
    
    saveCrashLog() {
        const logsDir = path.join(app.getPath('userData'), 'logs');
        if (!fs.existsSync(logsDir)) {
            fs.mkdirSync(logsDir, { recursive: true });
        }
        
        const logFile = path.join(logsDir, `crash-${Date.now()}.json`);
        fs.writeFileSync(logFile, JSON.stringify({
            crashes: this.crashLog,
            system: {
                platform: process.platform,
                arch: process.arch,
                nodeVersion: process.version,
                electronVersion: process.versions.electron
            }
        }, null, 2));
        
        console.log(`[BackendManager] Crash log saved to: ${logFile}`);
    }
    
    getCrashLog() {
        return this.crashLog;
    }
    
    resetRestartAttempts() {
        this.restartAttempts = 0;
        this.restartDelay = 3000;
        this.crashLog = [];
    }
}

module.exports = BackendManager;