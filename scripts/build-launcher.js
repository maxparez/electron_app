/**
 * Build script pro vytvoření launcher.exe
 * 
 * Tento script vytvoří samostatný launcher.exe, který bude:
 * 1. Spravovat Python backend
 * 2. Spouštět Electron frontend
 * 3. Řídit oba procesy
 */

const { execSync } = require('child_process');
const fs = require('fs-extra');
const path = require('path');

class LauncherBuilder {
    constructor() {
        this.projectRoot = path.resolve(__dirname, '..');
        this.buildDir = path.join(this.projectRoot, 'dist', 'launcher');
        this.launcherSource = path.join(this.projectRoot, 'src', 'launcher.js');
        this.packageJsonTemplate = {
            name: 'elektron-app-launcher',
            version: '1.0.0',
            description: 'ElektronApp Launcher',
            main: 'launcher.js',
            bin: {
                'launcher': './launcher.js'
            },
            dependencies: {
                'axios': '^1.9.0'
            },
            pkg: {
                scripts: ['launcher.js'],
                targets: ['node18-win-x64'],
                outputPath: '../launcher.exe'
            }
        };
    }

    log(message) {
        console.log(`[Launcher Builder] ${message}`);
    }

    async cleanup() {
        if (await fs.pathExists(this.buildDir)) {
            await fs.remove(this.buildDir);
            this.log('Vyčištěna build složka');
        }
    }

    async prepareBuildDir() {
        await fs.ensureDir(this.buildDir);
        this.log('Vytvořena build složka');

        // Zkopírovat launcher.js
        await fs.copy(this.launcherSource, path.join(this.buildDir, 'launcher.js'));
        this.log('Zkopírován launcher.js');

        // Vytvořit package.json
        await fs.writeJson(path.join(this.buildDir, 'package.json'), this.packageJsonTemplate, { spaces: 2 });
        this.log('Vytvořen package.json');
    }

    async installDependencies() {
        this.log('Instaluji závislosti...');
        
        const originalCwd = process.cwd();
        process.chdir(this.buildDir);
        
        try {
            execSync('npm install', { stdio: 'inherit' });
            this.log('Závislosti nainstalovány');
        } catch (error) {
            throw new Error(`Chyba při instalaci závislostí: ${error.message}`);
        } finally {
            process.chdir(originalCwd);
        }
    }

    async buildExecutable() {
        this.log('Vytvářím launcher.exe...');
        
        const originalCwd = process.cwd();
        process.chdir(this.buildDir);
        
        try {
            // Pokusíme se použít pkg
            try {
                execSync('npx pkg .', { stdio: 'inherit' });
                this.log('launcher.exe vytvořen pomocí pkg');
            } catch (pkgError) {
                this.log('pkg není dostupný, instaluji...');
                execSync('npm install -g pkg', { stdio: 'inherit' });
                execSync('npx pkg .', { stdio: 'inherit' });
                this.log('launcher.exe vytvořen');
            }
            
            // Přesunout launcher.exe do dist/
            const sourcePath = path.join(this.buildDir, 'launcher.exe');
            const targetPath = path.join(this.projectRoot, 'dist', 'launcher.exe');
            
            if (await fs.pathExists(sourcePath)) {
                await fs.move(sourcePath, targetPath);
                this.log(`launcher.exe přesunut do: ${targetPath}`);
            } else {
                throw new Error('launcher.exe nebyl vytvořen');
            }
            
        } catch (error) {
            throw new Error(`Chyba při vytváření executable: ${error.message}`);
        } finally {
            process.chdir(originalCwd);
        }
    }

    async createBatLauncher() {
        // Alternativní řešení - vytvořit .bat launcher pokud pkg nefunguje
        const batContent = `@echo off
cd /d "%~dp0"
node src\\launcher.js
pause`;
        
        const batPath = path.join(this.projectRoot, 'dist', 'launcher.bat');
        await fs.writeFile(batPath, batContent);
        this.log('Vytvořen launcher.bat jako fallback');
    }

    async build() {
        try {
            this.log('Začínám build launcher.exe...');
            
            // 1. Vyčistit a připravit
            await this.cleanup();
            await this.prepareBuildDir();
            
            // 2. Instalovat závislosti
            await this.installDependencies();
            
            // 3. Vytvořit executable
            try {
                await this.buildExecutable();
            } catch (error) {
                this.log(`Nepodařilo se vytvořit .exe: ${error.message}`);
                this.log('Vytvářím .bat launcher jako náhrada...');
                await this.createBatLauncher();
            }
            
            // 4. Cleanup
            await this.cleanup();
            
            this.log('✅ Build launcher dokončen!');
            this.log('Launcher je dostupný v dist/ složce');
            
        } catch (error) {
            this.log(`❌ Chyba při buildu: ${error.message}`);
            process.exit(1);
        }
    }
}

// Spustit build
if (require.main === module) {
    const builder = new LauncherBuilder();
    builder.build().catch(error => {
        console.error('Kritická chyba:', error);
        process.exit(1);
    });
}

module.exports = LauncherBuilder;