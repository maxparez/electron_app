const { app } = require('electron');
const path = require('path');
const fs = require('fs');

class Config {
    constructor() {
        this.configPath = path.join(app.getPath('userData'), 'config.json');
        this.data = this.load();
        this.isDev = process.argv.includes('--dev');
        
        // Load environment-specific config
        const envConfig = this.loadEnvironmentConfig();
        this.envConfig = envConfig;
    }

    loadEnvironmentConfig() {
        try {
            const configName = this.isDev ? 'development.json' : 'production.json';
            const envConfigPath = path.join(__dirname, '..', '..', 'config', configName);
            
            if (fs.existsSync(envConfigPath)) {
                const data = fs.readFileSync(envConfigPath, 'utf8');
                return JSON.parse(data);
            }
        } catch (error) {
            console.error('Error loading environment config:', error);
        }
        
        // Default configuration
        return {
            app: {
                name: "Nástroje pro ŠI a ŠII OP JAK",
                version: "1.0.0",
                debug: this.isDev
            },
            python: {
                debug: this.isDev,
                port: 5000,
                host: "127.0.0.1"
            },
            logging: {
                level: this.isDev ? "DEBUG" : "INFO",
                keepDays: this.isDev ? 7 : 30,
                maxFileSize: "10MB"
            },
            backend: {
                maxRestartAttempts: 5,
                restartDelay: 3000,
                healthCheckInterval: 30000
            }
        };
    }
    
    load() {
        try {
            if (fs.existsSync(this.configPath)) {
                const data = fs.readFileSync(this.configPath, 'utf8');
                return JSON.parse(data);
            }
        } catch (error) {
            console.error('Error loading config:', error);
        }
        return this.getDefaults();
    }

    save() {
        try {
            fs.writeFileSync(this.configPath, JSON.stringify(this.data, null, 2));
        } catch (error) {
            console.error('Error saving config:', error);
        }
    }

    getDefaults() {
        return {
            lastPlakatFolder: app.getPath('documents'),
            lastInvVzdFolder: app.getPath('documents'),
            lastZorSpecFolder: app.getPath('documents'),
            documentsPath: app.getPath('documents'),
            windowBounds: { width: 1200, height: 800 },
            language: 'cs'
        };
    }

    get(key, defaultValue = null) {
        // Check user config first
        if (this.data[key] !== undefined) {
            return this.data[key];
        }
        
        // Check defaults
        const defaults = this.getDefaults();
        if (defaults[key] !== undefined) {
            return defaults[key];
        }
        
        // Check environment config using dot notation
        const keys = key.split('.');
        let value = this.envConfig;
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                return defaultValue;
            }
        }
        
        return value !== undefined ? value : defaultValue;
    }

    set(key, value) {
        this.data[key] = value;
        this.save();
    }
    
    getEnv(path) {
        const keys = path.split('.');
        let value = this.envConfig;
        for (const key of keys) {
            if (value && typeof value === 'object' && key in value) {
                value = value[key];
            } else {
                return null;
            }
        }
        return value;
    }
}

module.exports = new Config();