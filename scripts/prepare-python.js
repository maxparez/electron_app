const fs = require('fs');
const path = require('path');
const https = require('https');
const { execSync } = require('child_process');
const AdmZip = require('adm-zip');

const PYTHON_VERSION = '3.11.9';
const PYTHON_URL = `https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-embed-amd64.zip`;
const PYTHON_DIR = path.join(__dirname, '..', 'python-embed');

async function downloadFile(url, dest) {
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(dest);
        https.get(url, (response) => {
            response.pipe(file);
            file.on('finish', () => {
                file.close(resolve);
            });
        }).on('error', (err) => {
            fs.unlink(dest, () => {});
            reject(err);
        });
    });
}

async function preparePython() {
    console.log('Preparing embedded Python...');
    
    // Create directory
    if (!fs.existsSync(PYTHON_DIR)) {
        fs.mkdirSync(PYTHON_DIR, { recursive: true });
    }
    
    const zipPath = path.join(PYTHON_DIR, 'python.zip');
    
    // Download Python if not exists
    if (!fs.existsSync(path.join(PYTHON_DIR, 'python.exe'))) {
        console.log('Downloading Python...');
        await downloadFile(PYTHON_URL, zipPath);
        
        console.log('Extracting Python...');
        const zip = new AdmZip(zipPath);
        zip.extractAllTo(PYTHON_DIR, true);
        
        // Clean up
        fs.unlinkSync(zipPath);
        
        // Enable site packages
        const pthFile = path.join(PYTHON_DIR, `python${PYTHON_VERSION.replace(/\./g, '')}._pth`);
        let content = fs.readFileSync(pthFile, 'utf8');
        content = content.replace('#import site', 'import site');
        fs.writeFileSync(pthFile, content);
    }
    
    // Download get-pip.py
    const getPipPath = path.join(PYTHON_DIR, 'get-pip.py');
    if (!fs.existsSync(getPipPath)) {
        console.log('Downloading pip...');
        await downloadFile('https://bootstrap.pypa.io/get-pip.py', getPipPath);
    }
    
    // Install pip
    const pipPath = path.join(PYTHON_DIR, 'Scripts', 'pip.exe');
    if (!fs.existsSync(pipPath)) {
        console.log('Installing pip...');
        execSync(`"${path.join(PYTHON_DIR, 'python.exe')}" "${getPipPath}"`, { 
            stdio: 'inherit',
            cwd: PYTHON_DIR 
        });
    }
    
    // Install required packages
    console.log('Installing Python packages...');
    const packages = ['flask', 'flask-cors', 'openpyxl', 'xlwings', 'pandas', 'reportlab'];
    
    // First upgrade pip
    execSync(`"${pipPath}" install --upgrade pip`, { 
        stdio: 'inherit',
        cwd: PYTHON_DIR 
    });
    
    // Install packages
    execSync(`"${pipPath}" install ${packages.join(' ')} --no-warn-script-location`, { 
        stdio: 'inherit',
        cwd: PYTHON_DIR 
    });
    
    console.log('Python preparation complete!');
}

preparePython().catch(console.error);