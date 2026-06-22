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

function parseChangelogReleaseHistory(changelogText, limit = 5) {
    const releases = [];
    let currentRelease = null;
    let currentSection = null;

    changelogText.split(/\r?\n/).forEach((line) => {
        const releaseMatch = /^## \[([^\]]+)\](?: - (.+))?/.exec(line);
        if (releaseMatch) {
            currentRelease = {
                version: releaseMatch[1],
                date: releaseMatch[2] || '',
                sections: []
            };
            releases.push(currentRelease);
            currentSection = null;
            return;
        }

        if (!currentRelease) {
            return;
        }

        const sectionMatch = /^###\s+(.+)/.exec(line);
        if (sectionMatch) {
            currentSection = {
                title: sectionMatch[1].replace(/^[^\p{L}\p{N}]+/u, '').trim(),
                items: []
            };
            currentRelease.sections.push(currentSection);
            return;
        }

        const itemMatch = /^-\s+(?:\*\*([^*]+)\*\*:?\s*)?(.+)/.exec(line);
        if (itemMatch && currentSection) {
            currentSection.items.push({
                title: (itemMatch[1] || itemMatch[2]).trim(),
                description: itemMatch[1] ? itemMatch[2].trim() : ''
            });
        }
    });

    return releases.slice(0, limit);
}

function readReleaseHistory(repoRoot, limit = 5) {
    try {
        const changelogPath = path.join(repoRoot, 'CHANGELOG.md');
        if (!fs.existsSync(changelogPath)) {
            return [];
        }
        return parseChangelogReleaseHistory(
            fs.readFileSync(changelogPath, 'utf8'),
            limit
        );
    } catch (error) {
        return [];
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
        releaseNotes,
        releaseHistory: readReleaseHistory(root, 5)
    };
}

module.exports = {
    parseChangelogReleaseHistory,
    readAboutInfo
};
