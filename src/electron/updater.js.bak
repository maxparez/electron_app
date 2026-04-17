const { app, dialog, shell } = require('electron');
const { autoUpdater } = require('electron-updater');
const path = require('path');
const fs = require('fs');
const axios = require('axios');
const config = require('./config');

class Updater {
    constructor() {
        this.mainWindow = null;
        this.updateAvailable = false;
        this.downloadProgress = 0;
        this.updateInfo = null;
        
        // Configure auto-updater
        autoUpdater.autoDownload = false;
        autoUpdater.autoInstallOnAppQuit = true;
        
        // Set up event handlers
        this.setupEventHandlers();
    }
    
    setMainWindow(window) {
        this.mainWindow = window;
    }
    
    setupEventHandlers() {
        autoUpdater.on('checking-for-update', () => {
            console.log('[Updater] Checking for updates...');
            this.sendStatusToWindow('checking-for-update');
        });
        
        autoUpdater.on('update-available', (info) => {
            console.log('[Updater] Update available:', info.version);
            this.updateAvailable = true;
            this.updateInfo = info;
            this.sendStatusToWindow('update-available', info);
            
            // Show dialog to user
            this.showUpdateDialog(info);
        });
        
        autoUpdater.on('update-not-available', (info) => {
            console.log('[Updater] Update not available');
            this.sendStatusToWindow('update-not-available', info);
        });
        
        autoUpdater.on('error', (err) => {
            console.error('[Updater] Error:', err);
            this.sendStatusToWindow('error', err.message);
        });
        
        autoUpdater.on('download-progress', (progressObj) => {
            this.downloadProgress = progressObj.percent;
            console.log(`[Updater] Download progress: ${progressObj.percent}%`);
            this.sendStatusToWindow('download-progress', progressObj);
        });
        
        autoUpdater.on('update-downloaded', (info) => {
            console.log('[Updater] Update downloaded');
            this.sendStatusToWindow('update-downloaded', info);
            
            // Show restart dialog
            this.showRestartDialog();
        });
    }
    
    async checkForUpdates() {
        try {
            if (!config.get('updates.autoCheck', true)) {
                console.log('[Updater] Auto-check disabled');
                return;
            }
            
            // For GitHub releases
            const updateUrl = config.get('updates.updateUrl');
            if (updateUrl && updateUrl.includes('github.com')) {
                await this.checkGitHubUpdates(updateUrl);
            } else {
                // Use electron-updater for other sources
                await autoUpdater.checkForUpdates();
            }
        } catch (error) {
            console.error('[Updater] Failed to check for updates:', error);
        }
    }
    
    async checkGitHubUpdates(updateUrl) {
        try {
            const response = await axios.get(updateUrl);
            const latestRelease = response.data;
            const latestVersion = latestRelease.tag_name.replace('v', '');
            const currentVersion = app.getVersion();
            
            console.log(`[Updater] Current version: ${currentVersion}, Latest: ${latestVersion}`);
            
            if (this.compareVersions(latestVersion, currentVersion) > 0) {
                // Find Windows installer asset
                const asset = latestRelease.assets.find(a => 
                    a.name.endsWith('.exe') || a.name.endsWith('.msi')
                );
                
                if (asset) {
                    this.updateInfo = {
                        version: latestVersion,
                        releaseNotes: latestRelease.body,
                        releaseDate: latestRelease.published_at,
                        downloadUrl: asset.browser_download_url,
                        fileName: asset.name,
                        fileSize: asset.size
                    };
                    
                    this.updateAvailable = true;
                    this.sendStatusToWindow('update-available', this.updateInfo);
                    this.showUpdateDialog(this.updateInfo);
                }
            } else {
                this.sendStatusToWindow('update-not-available', { version: currentVersion });
            }
        } catch (error) {
            console.error('[Updater] GitHub check failed:', error);
            this.sendStatusToWindow('error', error.message);
        }
    }
    
    compareVersions(v1, v2) {
        const parts1 = v1.split('.').map(Number);
        const parts2 = v2.split('.').map(Number);
        
        for (let i = 0; i < Math.max(parts1.length, parts2.length); i++) {
            const part1 = parts1[i] || 0;
            const part2 = parts2[i] || 0;
            
            if (part1 > part2) return 1;
            if (part1 < part2) return -1;
        }
        
        return 0;
    }
    
    async showUpdateDialog(info) {
        const result = await dialog.showMessageBox(this.mainWindow, {
            type: 'info',
            title: 'Dostupná aktualizace',
            message: `Nová verze ${info.version} je k dispozici`,
            detail: `Aktuální verze: ${app.getVersion()}\nNová verze: ${info.version}\n\n${info.releaseNotes || 'Žádné poznámky k vydání'}`,
            buttons: ['Stáhnout a nainstalovat', 'Později'],
            defaultId: 0,
            cancelId: 1
        });
        
        if (result.response === 0) {
            if (info.downloadUrl) {
                // Download from GitHub
                await this.downloadGitHubUpdate(info);
            } else {
                // Use electron-updater
                autoUpdater.downloadUpdate();
            }
        }
    }
    
    async downloadGitHubUpdate(info) {
        try {
            const downloadsPath = app.getPath('downloads');
            const filePath = path.join(downloadsPath, info.fileName);
            
            // Show save dialog
            const result = await dialog.showSaveDialog(this.mainWindow, {
                defaultPath: filePath,
                filters: [
                    { name: 'Instalační soubor', extensions: ['exe', 'msi'] }
                ]
            });
            
            if (!result.canceled) {
                this.sendStatusToWindow('download-started', info);
                
                // Download file
                const response = await axios({
                    method: 'GET',
                    url: info.downloadUrl,
                    responseType: 'stream',
                    onDownloadProgress: (progressEvent) => {
                        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                        this.downloadProgress = percentCompleted;
                        this.sendStatusToWindow('download-progress', { percent: percentCompleted });
                    }
                });
                
                // Save to file
                const writer = fs.createWriteStream(result.filePath);
                response.data.pipe(writer);
                
                writer.on('finish', () => {
                    this.sendStatusToWindow('download-complete', { filePath: result.filePath });
                    
                    // Ask to install
                    dialog.showMessageBox(this.mainWindow, {
                        type: 'info',
                        title: 'Stažení dokončeno',
                        message: 'Aktualizace byla stažena',
                        detail: 'Chcete nyní spustit instalaci?',
                        buttons: ['Spustit instalaci', 'Později'],
                        defaultId: 0
                    }).then((result) => {
                        if (result.response === 0) {
                            shell.openPath(result.filePath);
                            app.quit();
                        }
                    });
                });
                
                writer.on('error', (error) => {
                    console.error('[Updater] Download error:', error);
                    this.sendStatusToWindow('error', error.message);
                });
            }
        } catch (error) {
            console.error('[Updater] Download failed:', error);
            this.sendStatusToWindow('error', error.message);
        }
    }
    
    async showRestartDialog() {
        const result = await dialog.showMessageBox(this.mainWindow, {
            type: 'info',
            title: 'Aktualizace připravena',
            message: 'Aktualizace byla stažena a je připravena k instalaci',
            detail: 'Aplikace se musí restartovat pro dokončení aktualizace.',
            buttons: ['Restartovat nyní', 'Později'],
            defaultId: 0,
            cancelId: 1
        });
        
        if (result.response === 0) {
            autoUpdater.quitAndInstall();
        }
    }
    
    sendStatusToWindow(status, data = null) {
        if (this.mainWindow && !this.mainWindow.isDestroyed()) {
            this.mainWindow.webContents.send('update-status', { status, data });
        }
    }
    
    // Manual check for updates
    async checkManually() {
        this.sendStatusToWindow('checking-for-update');
        await this.checkForUpdates();
        
        if (!this.updateAvailable) {
            dialog.showMessageBox(this.mainWindow, {
                type: 'info',
                title: 'Žádné aktualizace',
                message: 'Aplikace je aktuální',
                detail: `Používáte nejnovější verzi ${app.getVersion()}`
            });
        }
    }
}

module.exports = Updater;