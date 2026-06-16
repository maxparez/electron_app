#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const shouldRepairPath = process.argv.includes('--repair-path');
const repoRoot = process.cwd();
const electronDir = path.join(repoRoot, 'node_modules', 'electron');
const distDir = path.join(electronDir, 'dist');
const pathFile = path.join(electronDir, 'path.txt');
const defaultExecutable = process.platform === 'win32' ? 'electron.exe' : 'electron';

function fail(message) {
    process.stderr.write(`${message}\n`);
    process.exit(1);
}

if (!fs.existsSync(electronDir)) {
    fail(`Electron package directory is missing: ${electronDir}`);
}

let rawPath = '';
if (fs.existsSync(pathFile)) {
    rawPath = fs.readFileSync(pathFile, 'utf-8');
}

const executablePath = (rawPath || defaultExecutable).trim();
if (!executablePath) {
    fail(`Electron path.txt is empty: ${pathFile}`);
}

const electronExecutable = path.join(distDir, executablePath);
if (!fs.existsSync(electronExecutable)) {
    fail(`Missing Electron executable: ${electronExecutable}`);
}

if (shouldRepairPath && rawPath !== executablePath) {
    fs.writeFileSync(pathFile, executablePath, { encoding: 'ascii' });
}

process.stdout.write(`${electronExecutable}\n`);
