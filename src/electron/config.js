const { app } = require('electron');
const path = require('path');
const fs = require('fs');

class Config {
    constructor() {
        this.configPath = path.join(app.getPath('userData'), 'config.json');
        this.data = this.load();
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

    get(key) {
        return this.data[key] || this.getDefaults()[key];
    }

    set(key, value) {
        this.data[key] = value;
        this.save();
    }
}

module.exports = new Config();