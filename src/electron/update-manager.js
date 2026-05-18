const { execFileSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const DEFAULT_BRANCH = 'windows-install';
const DEFAULT_CHANNEL = 'stable';

function loadChannelConfig(repoRoot) {
    const configPath = path.join(repoRoot, 'channel-config.json');
    if (!fs.existsSync(configPath)) {
        return { branch: DEFAULT_BRANCH, channel: DEFAULT_CHANNEL, debug_logging: false };
    }

    try {
        const rawConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        return {
            branch: rawConfig.branch || DEFAULT_BRANCH,
            channel: rawConfig.channel || DEFAULT_CHANNEL,
            debug_logging: Boolean(rawConfig.debug_logging)
        };
    } catch (error) {
        return { branch: DEFAULT_BRANCH, channel: DEFAULT_CHANNEL, debug_logging: false };
    }
}

function createGitExecutor(repoRoot) {
    return (args) => execFileSync('git', args, {
        cwd: repoRoot,
        encoding: 'utf8',
        windowsHide: true,
        timeout: 60000
    });
}

function checkForUpdate({ repoRoot, channelConfig = null, execGit = null } = {}) {
    if (!repoRoot) {
        throw new Error('Repozitář aplikace nebyl nalezen.');
    }

    const config = channelConfig || loadChannelConfig(repoRoot);
    const branch = config.branch || DEFAULT_BRANCH;
    const channel = config.channel || DEFAULT_CHANNEL;
    const runGit = execGit || createGitExecutor(repoRoot);
    const remoteRef = `origin/${branch}`;

    runGit(['fetch', 'origin', branch]);
    const localCommit = runGit(['rev-parse', 'HEAD']).trim();
    const remoteCommit = runGit(['rev-parse', remoteRef]).trim();
    const latestSummary = runGit([
        'log',
        '-1',
        '--format=%h %cd %s',
        '--date=short',
        remoteRef
    ]).trim();

    return {
        updateAvailable: localCommit !== remoteCommit,
        branch,
        channel,
        localCommit,
        remoteCommit,
        latestSummary
    };
}

function startUpdate({
    repoRoot,
    platform = process.platform,
    fileExists = fs.existsSync,
    spawnDetached = null
} = {}) {
    if (platform !== 'win32') {
        return {
            success: false,
            message: 'Spuštění aktualizace z aplikace je podporované jen na Windows.'
        };
    }

    const scriptName = 'update-windows.bat';
    const scriptPath = path.join(repoRoot || '', scriptName);
    if (!repoRoot || !fileExists(scriptPath)) {
        return {
            success: false,
            message: 'Nenalezen update-windows.bat v instalační složce aplikace.'
        };
    }

    const launcher = spawnDetached || ((command, args, options) => {
        const child = spawn(command, args, options);
        child.unref();
    });

    launcher('cmd.exe', ['/d', '/k', scriptName], {
        cwd: repoRoot,
        detached: true,
        stdio: 'ignore',
        windowsHide: false
    });

    return {
        success: true,
        message: 'Aktualizace byla spuštěna v novém okně. Aplikace se ukončí.'
    };
}

function findRepoRoot(startPaths, fileExists = fs.existsSync) {
    for (const startPath of startPaths.filter(Boolean)) {
        let current = path.resolve(startPath);
        while (current && current !== path.dirname(current)) {
            if (
                fileExists(path.join(current, '.git')) &&
                fileExists(path.join(current, 'update-windows.bat'))
            ) {
                return current;
            }
            current = path.dirname(current);
        }
    }
    return null;
}

module.exports = {
    checkForUpdate,
    findRepoRoot,
    loadChannelConfig,
    startUpdate
};
