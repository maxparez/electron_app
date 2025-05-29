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
                // In production, use bundled Python from resources
                pythonPath = path.join(process.resourcesPath, 'python', 'python.exe');
                
                if (!fs.existsSync(pythonPath)) {
                    throw new Error(`Bundled Python not found at: ${pythonPath}`);
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
            
            const scriptPath = isProd 
                ? path.join(process.resourcesPath, 'app.asar.unpacked', 'src', 'python', 'server.py')
                : path.join(appPath, 'src', 'python', 'server.py');
            
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