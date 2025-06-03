const { execSync } = require('child_process');
const fs = require('fs-extra');
const path = require('path');

async function build() {
    console.log('Building Windows application with embedded Python...');
    
    const projectRoot = path.join(__dirname, '..');
    const pythonEmbedDir = path.join(projectRoot, 'python-embed');
    
    // 1. Prepare Python
    console.log('1. Preparing Python...');
    execSync('node scripts/prepare-python.js', { 
        stdio: 'inherit',
        cwd: projectRoot 
    });
    
    // 2. Copy Python to resources
    console.log('2. Copying Python to resources...');
    const resourcesDir = path.join(projectRoot, 'resources');
    const targetPythonDir = path.join(resourcesDir, 'python');
    
    // Clean and create directories
    fs.removeSync(targetPythonDir);
    fs.ensureDirSync(targetPythonDir);
    
    // Copy Python embed
    fs.copySync(pythonEmbedDir, targetPythonDir);
    
    // 3. Update forge config to include Python
    console.log('3. Updating forge config...');
    const forgeConfig = require('../forge.config.js');
    
    // Add extraResource
    if (!forgeConfig.packagerConfig.extraResource) {
        forgeConfig.packagerConfig.extraResource = [];
    }
    forgeConfig.packagerConfig.extraResource.push('./resources/python');
    
    // Write updated config
    const configContent = `module.exports = ${JSON.stringify(forgeConfig, null, 2)};`;
    fs.writeFileSync(
        path.join(projectRoot, 'forge.config.temp.js'), 
        configContent
    );
    
    // 4. Build with Electron Forge
    console.log('4. Building with Electron Forge...');
    try {
        execSync('npm run make', { 
            stdio: 'inherit',
            cwd: projectRoot,
            env: {
                ...process.env,
                ELECTRON_FORGE_CONFIG: 'forge.config.temp.js'
            }
        });
    } finally {
        // Clean up temp config
        fs.removeSync(path.join(projectRoot, 'forge.config.temp.js'));
    }
    
    console.log('Build complete!');
}

build().catch(console.error);