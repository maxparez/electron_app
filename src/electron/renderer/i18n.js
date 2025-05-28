// Simple i18n module for Czech localization

class I18n {
    constructor() {
        this.translations = {};
        this.currentLocale = 'cs';
    }
    
    // Load translations from JSON
    async load(locale = 'cs') {
        try {
            const response = await fetch(`./locales/${locale}.json`);
            if (!response.ok) {
                throw new Error(`Failed to load locale: ${locale}`);
            }
            this.translations = await response.json();
            this.currentLocale = locale;
            return true;
        } catch (error) {
            console.error('Failed to load translations:', error);
            return false;
        }
    }
    
    // Get translation by key (supports nested keys like 'app.title')
    t(key, params = {}) {
        const keys = key.split('.');
        let value = this.translations;
        
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                console.warn(`Translation not found: ${key}`);
                return key;
            }
        }
        
        // Replace parameters like {{name}} with actual values
        if (typeof value === 'string') {
            return value.replace(/\{\{(\w+)\}\}/g, (match, param) => {
                return params[param] || match;
            });
        }
        
        return value;
    }
    
    // Apply translations to DOM elements with data-i18n attribute
    translatePage() {
        // Translate elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key);
            
            if (element.tagName === 'INPUT' && element.hasAttribute('placeholder')) {
                element.placeholder = translation;
            } else if (element.tagName === 'INPUT' && element.type === 'button') {
                element.value = translation;
            } else {
                element.textContent = translation;
            }
        });
        
        // Translate elements with data-i18n-placeholder attribute
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            element.placeholder = this.t(key);
        });
        
        // Update document title
        document.title = this.t('app.title');
    }
}

// Create global instance
const i18n = new I18n();

// Export for use in other modules
window.i18n = i18n;