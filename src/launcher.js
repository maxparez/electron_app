/**
 * ElektronApp Launcher
 * 
 * Hlavní spouštěč aplikace, který:
 * 1. Zkontroluje a spustí Python backend
 * 2. Spustí Electron frontend
 * 3. Správně ukončí oba procesy při zavření
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const axios = require('axios');

class ElektronAppLauncher {
    constructor() {
        this.backendProcess = null;
        this.frontendProcess = null;
        this.backendPort = 5000;
        this.backendUrl = `http://localhost:${this.backendPort}`;
        this.maxStartupTime = 15000; // 15 sekund na startup
        this.healthCheckInterval = 500; // Check každých 500ms
        
        // Cesty k důležitým souborům
        this.pythonEnvPath = path.join(__dirname, '..', 'electron-app-env');
        this.pythonExe = path.join(this.pythonEnvPath, 'Scripts', 'python.exe');
        this.backendScript = path.join(__dirname, 'python', 'server.py');
        this.electronExe = path.join(__dirname, '..', 'electron-app.exe');
        
        // Bind metody
        this.cleanup = this.cleanup.bind(this);
    }

    log(message) {
        const timestamp = new Date().toLocaleTimeString();
        console.log(`[${timestamp}] ${message}`);
    }

    error(message) {
        const timestamp = new Date().toLocaleTimeString();
        console.error(`[${timestamp}] ❌ ${message}`);
    }

    success(message) {
        const timestamp = new Date().toLocaleTimeString();
        console.log(`[${timestamp}] ✅ ${message}`);
    }

    async checkFile(filePath, description) {
        if (!fs.existsSync(filePath)) {
            this.error(`${description} nebyl nalezen: ${filePath}`);
            return false;
        }
        this.log(`${description} nalezen: ${path.basename(filePath)}`);
        return true;
    }

    async validateEnvironment() {
        this.log('Kontroluji prostředí...');
        
        // Kontrola Python prostředí
        if (!await this.checkFile(this.pythonExe, 'Python prostředí')) {
            this.error('Python prostředí nenalezeno!');
            this.error('Spusťte prosím "python-backend-install.bat" pro instalaci backendu.');
            return false;
        }

        // Kontrola backend scriptu
        if (!await this.checkFile(this.backendScript, 'Backend script')) {
            return false;
        }

        // Kontrola frontend
        if (!await this.checkFile(this.electronExe, 'Frontend aplikace')) {
            return false;
        }

        this.success('Prostředí je v pořádku');
        return true;
    }

    async checkBackendHealth() {
        try {
            const response = await axios.get(`${this.backendUrl}/health`, { 
                timeout: 1000 
            });
            return response.status === 200;
        } catch (error) {
            return false;
        }
    }

    async waitForBackend() {
        this.log('Čekám na spuštění backendu...');
        
        const startTime = Date.now();
        
        while (Date.now() - startTime < this.maxStartupTime) {
            if (await this.checkBackendHealth()) {
                this.success('Backend je připraven');
                return true;
            }
            
            // Krátká pauza před dalším pokusem
            await new Promise(resolve => setTimeout(resolve, this.healthCheckInterval));
        }
        
        this.error('Backend se nepodařilo spustit včas');
        return false;
    }

    async startBackend() {
        this.log('Spouštím Python backend...');
        
        // Nejdříve zkontroluj, zda už backend neběží
        if (await this.checkBackendHealth()) {
            this.success('Backend již běží');
            return true;
        }

        // Spusť Python backend
        this.backendProcess = spawn(this.pythonExe, [this.backendScript], {
            cwd: path.dirname(this.backendScript),
            stdio: ['ignore', 'pipe', 'pipe'],
            windowsHide: true // Skryj konzoli na Windows
        });

        // Log výstupu pro debugging
        this.backendProcess.stdout.on('data', (data) => {
            this.log(`Backend: ${data.toString().trim()}`);
        });

        this.backendProcess.stderr.on('data', (data) => {
            this.error(`Backend: ${data.toString().trim()}`);
        });

        this.backendProcess.on('error', (error) => {
            this.error(`Chyba při spuštění backendu: ${error.message}`);
        });

        this.backendProcess.on('exit', (code) => {
            if (code !== 0) {
                this.error(`Backend ukončen s kódem: ${code}`);
            }
        });

        // Počkej na spuštění
        return await this.waitForBackend();
    }

    async startFrontend() {
        this.log('Spouštím Electron frontend...');
        
        this.frontendProcess = spawn(this.electronExe, [], {
            stdio: ['ignore', 'pipe', 'pipe'],
            windowsHide: false // Frontend chceme vidět
        });

        this.frontendProcess.stdout.on('data', (data) => {
            this.log(`Frontend: ${data.toString().trim()}`);
        });

        this.frontendProcess.stderr.on('data', (data) => {
            this.error(`Frontend: ${data.toString().trim()}`);
        });

        this.frontendProcess.on('error', (error) => {
            this.error(`Chyba při spuštění frontendu: ${error.message}`);
            this.cleanup();
        });

        this.frontendProcess.on('exit', (code) => {
            this.log(`Frontend ukončen s kódem: ${code}`);
            this.cleanup();
        });

        this.success('Frontend spuštěn');
        return true;
    }

    cleanup() {
        this.log('Ukončuji aplikaci...');
        
        // Ukončení frontend procesu
        if (this.frontendProcess && !this.frontendProcess.killed) {
            this.log('Ukončuji frontend...');
            this.frontendProcess.kill('SIGTERM');
        }
        
        // Ukončení backend procesu
        if (this.backendProcess && !this.backendProcess.killed) {
            this.log('Ukončuji backend...');
            this.backendProcess.kill('SIGTERM');
            
            // Pokud se neukončí do 5 sekund, force kill
            setTimeout(() => {
                if (this.backendProcess && !this.backendProcess.killed) {
                    this.log('Vynucuji ukončení backendu...');
                    this.backendProcess.kill('SIGKILL');
                }
            }, 5000);
        }
        
        this.success('Aplikace ukončena');
    }

    setupExitHandlers() {
        // Zachycení různých způsobů ukončení
        process.on('SIGINT', this.cleanup);
        process.on('SIGTERM', this.cleanup);
        process.on('exit', this.cleanup);
        
        // Windows specifické
        if (process.platform === 'win32') {
            require('readline').createInterface({
                input: process.stdin,
                output: process.stdout
            }).on('SIGINT', this.cleanup);
        }
    }

    async launch() {
        console.log('========================================');
        console.log('        ElektronApp Launcher');
        console.log('========================================');
        console.log('');

        // Setup cleanup handlers
        this.setupExitHandlers();

        try {
            // 1. Validace prostředí
            if (!await this.validateEnvironment()) {
                process.exit(1);
            }

            // 2. Spuštění backendu
            if (!await this.startBackend()) {
                this.error('Nepodařilo se spustit backend');
                process.exit(1);
            }

            // 3. Spuštění frontendu
            if (!await this.startFrontend()) {
                this.error('Nepodařilo se spustit frontend');
                this.cleanup();
                process.exit(1);
            }

            this.success('ElektronApp úspěšně spuštěn!');
            this.log('Pro ukončení aplikace zavřete hlavní okno nebo stiskněte Ctrl+C');

        } catch (error) {
            this.error(`Neočekávaná chyba: ${error.message}`);
            this.cleanup();
            process.exit(1);
        }
    }
}

// Spuštění aplikace
if (require.main === module) {
    const launcher = new ElektronAppLauncher();
    launcher.launch().catch(error => {
        console.error('Kritická chyba:', error);
        process.exit(1);
    });
}

module.exports = ElektronAppLauncher;