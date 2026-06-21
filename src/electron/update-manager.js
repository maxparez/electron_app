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

function readGitJson(runGit, objectSpec) {
    try {
        const rawValue = runGit(['show', objectSpec]);
        return JSON.parse(rawValue);
    } catch (error) {
        return null;
    }
}

function compareVersions(leftVersion, rightVersion) {
    const parseVersion = (version) => {
        const match = /^(\d+)\.(\d+)\.(\d+)/.exec(version || '');
        return match ? match.slice(1).map(Number) : null;
    };
    const left = parseVersion(leftVersion);
    const right = parseVersion(rightVersion);
    if (!left || !right) {
        return 0;
    }
    for (let index = 0; index < 3; index += 1) {
        if (left[index] !== right[index]) {
            return left[index] > right[index] ? 1 : -1;
        }
    }
    return 0;
}

function resolveActiveBranch(runGit, configuredBranch) {
    try {
        const checkedOutBranch = runGit(['branch', '--show-current']).trim();
        return checkedOutBranch || configuredBranch;
    } catch (error) {
        return configuredBranch;
    }
}

function checkForUpdate({ repoRoot, channelConfig = null, execGit = null } = {}) {
    if (!repoRoot) {
        throw new Error('Repozitář aplikace nebyl nalezen.');
    }

    const config = channelConfig || loadChannelConfig(repoRoot);
    const runGit = execGit || createGitExecutor(repoRoot);
    const configuredBranch = config.branch || DEFAULT_BRANCH;
    const branch = resolveActiveBranch(runGit, configuredBranch);
    const channel = branch !== configuredBranch ? 'test' : (config.channel || DEFAULT_CHANNEL);
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
    const localPackage = readGitJson(runGit, 'HEAD:package.json');
    const remotePackage = readGitJson(runGit, `${remoteRef}:package.json`);
    const remoteReleaseNotes = readGitJson(runGit, `${remoteRef}:release-notes.json`);
    const releaseNotes = (
        remoteReleaseNotes?.version &&
        remoteReleaseNotes?.sections &&
        remoteReleaseNotes.version === remotePackage?.version &&
        remoteReleaseNotes.version !== localPackage?.version
    ) ? remoteReleaseNotes : null;
    const downgradeBlocked = Boolean(
        localPackage?.version &&
        remotePackage?.version &&
        compareVersions(remotePackage.version, localPackage.version) < 0
    );

    return {
        updateAvailable: localCommit !== remoteCommit && !downgradeBlocked,
        branch,
        channel,
        localCommit,
        remoteCommit,
        latestSummary,
        currentVersion: localPackage?.version || null,
        latestVersion: remotePackage?.version || releaseNotes?.version || null,
        releaseNotes,
        downgradeBlocked
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
    compareVersions,
    findRepoRoot,
    loadChannelConfig,
    startUpdate
};
