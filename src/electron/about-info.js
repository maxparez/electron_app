const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const DEFAULT_CHANNEL = {
    channel: 'stable',
    branch: 'windows-install',
    debug_logging: false
};

function readJsonIfExists(filePath, fallback = null) {
    try {
        if (!fs.existsSync(filePath)) {
            return fallback;
        }
        return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } catch (error) {
        return fallback;
    }
}

function runGit(args, repoRoot) {
    return execFileSync('git', args, {
        cwd: repoRoot,
        encoding: 'utf8',
        stdio: ['ignore', 'pipe', 'ignore']
    }).trim();
}

function readGitInfo(repoRoot, execGit = null) {
    const git = execGit || ((args) => runGit(args, repoRoot));

    try {
        return {
            commit: git(['rev-parse', '--short', 'HEAD']).trim(),
            branch: git(['rev-parse', '--abbrev-ref', 'HEAD']).trim(),
            date: git(['log', '-1', '--format=%cd', '--date=short']).trim()
        };
    } catch (error) {
        return {
            commit: null,
            branch: null,
            date: null
        };
    }
}

function readAboutInfo({ repoRoot, execGit = null } = {}) {
    const root = repoRoot || process.cwd();
    const packageJson = readJsonIfExists(path.join(root, 'package.json'), {});
    const productionConfig = readJsonIfExists(path.join(root, 'config', 'production.json'), {});
    const channelConfig = readJsonIfExists(path.join(root, 'channel-config.json'), DEFAULT_CHANNEL);
    const releaseNotes = readJsonIfExists(path.join(root, 'release-notes.json'), null);
    const version = packageJson.version || productionConfig?.app?.version || 'neuvedena';

    return {
        name: productionConfig?.app?.name || packageJson.name || 'Nástroje pro ŠI a ŠII OP JAK',
        version,
        channel: {
            ...DEFAULT_CHANNEL,
            ...(channelConfig || {})
        },
        git: readGitInfo(root, execGit),
        releaseNotes
    };
}

module.exports = {
    readAboutInfo
};
