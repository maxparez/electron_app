#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const RELEASE_TYPES = new Set(['patch', 'minor', 'major']);
const SECTION_CONFIG = {
    feature: { key: 'features', title: 'Nové funkce' },
    improvement: { key: 'improvements', title: 'Vylepšení' },
    fix: { key: 'fixes', title: 'Opravy' }
};

function determineReleaseType(changes, override = null) {
    if (override) {
        if (!RELEASE_TYPES.has(override)) {
            throw new Error(`Neplatný typ vydání: ${override}`);
        }
        return override;
    }
    if (changes.some((change) => change.breaking)) {
        return 'major';
    }
    if (changes.some((change) => change.type === 'feature')) {
        return 'minor';
    }
    return 'patch';
}

function bumpVersion(version, releaseType) {
    const match = /^(\d+)\.(\d+)\.(\d+)$/.exec(version);
    if (!match || !RELEASE_TYPES.has(releaseType)) {
        throw new Error(`Nelze zvýšit verzi ${version} jako ${releaseType}`);
    }

    let major = Number(match[1]);
    let minor = Number(match[2]);
    let patch = Number(match[3]);
    if (releaseType === 'major') {
        major += 1;
        minor = 0;
        patch = 0;
    } else if (releaseType === 'minor') {
        minor += 1;
        patch = 0;
    } else {
        patch += 1;
    }
    return `${major}.${minor}.${patch}`;
}

function readJson(filePath) {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function writeJson(filePath, value) {
    fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

function loadChangeFragments(changesDir) {
    if (!fs.existsSync(changesDir)) {
        return [];
    }

    return fs.readdirSync(changesDir)
        .filter((name) => name.endsWith('.json'))
        .sort()
        .map((name) => {
            const filePath = path.join(changesDir, name);
            const change = readJson(filePath);
            if (!SECTION_CONFIG[change.type] || !change.title || !change.description) {
                throw new Error(`Neplatný change fragment: ${name}`);
            }
            return {
                type: change.type,
                title: String(change.title).trim(),
                description: String(change.description).trim(),
                breaking: Boolean(change.breaking),
                filePath
            };
        });
}

function groupChanges(changes) {
    const sections = {
        features: [],
        improvements: [],
        fixes: []
    };
    for (const change of changes) {
        const section = SECTION_CONFIG[change.type];
        sections[section.key].push({
            title: change.title,
            description: change.description,
            ...(change.breaking ? { breaking: true } : {})
        });
    }
    return sections;
}

function buildSummary(version, sections) {
    const parts = [];
    if (sections.features.length) {
        const count = sections.features.length;
        const label = count === 1 ? 'nová funkce' : count < 5 ? 'nové funkce' : 'nových funkcí';
        parts.push(`${count} ${label}`);
    }
    if (sections.improvements.length) {
        parts.push(`${sections.improvements.length} vylepšení`);
    }
    if (sections.fixes.length) {
        const count = sections.fixes.length;
        const label = count === 1 ? 'oprava' : count < 5 ? 'opravy' : 'oprav';
        parts.push(`${count} ${label}`);
    }
    const lastPart = parts.pop();
    const joinedParts = parts.length ? `${parts.join(', ')} a ${lastPart}` : lastPart;
    return `Verze ${version}: ${joinedParts}.`;
}

function renderChangelogEntry(version, date, sections) {
    const lines = [`## [${version}] - ${date}`, ''];
    for (const config of Object.values(SECTION_CONFIG)) {
        const items = sections[config.key];
        if (!items.length) {
            continue;
        }
        lines.push(`### ${config.title}`, '');
        for (const item of items) {
            const marker = item.breaking ? ' **Nekompatibilní změna.**' : '';
            lines.push(`- **${item.title}**: ${item.description}${marker}`);
        }
        lines.push('');
    }
    return `${lines.join('\n').trim()}\n`;
}

function prependChangelog(changelog, entry) {
    const firstReleaseIndex = changelog.search(/^## \[/m);
    if (firstReleaseIndex === -1) {
        return `${changelog.trimEnd()}\n\n${entry}`;
    }
    return `${changelog.slice(0, firstReleaseIndex).trimEnd()}\n\n${entry}\n${changelog.slice(firstReleaseIndex)}`;
}

function updateVersionFiles(rootDir, version) {
    const packagePath = path.join(rootDir, 'package.json');
    const packageJson = readJson(packagePath);
    packageJson.version = version;
    writeJson(packagePath, packageJson);

    const lockPath = path.join(rootDir, 'package-lock.json');
    const packageLock = readJson(lockPath);
    packageLock.version = version;
    if (packageLock.packages && packageLock.packages['']) {
        packageLock.packages[''].version = version;
    }
    writeJson(lockPath, packageLock);

    for (const [filename, configuredVersion] of [
        ['production.json', version],
        ['development.json', `${version}-dev`]
    ]) {
        const configPath = path.join(rootDir, 'config', filename);
        const config = readJson(configPath);
        config.app.version = configuredVersion;
        writeJson(configPath, config);
    }

    const electronConfigPath = path.join(rootDir, 'src', 'electron', 'config.js');
    const electronConfig = fs.readFileSync(electronConfigPath, 'utf8');
    const updatedElectronConfig = electronConfig.replace(
        /version:\s*"\d+\.\d+\.\d+"/,
        `version: "${version}"`
    );
    if (updatedElectronConfig === electronConfig) {
        throw new Error('Verze v src/electron/config.js nebyla nalezena');
    }
    fs.writeFileSync(electronConfigPath, updatedElectronConfig, 'utf8');
}

function prepareRelease({
    rootDir = process.cwd(),
    releaseType = null,
    date = new Date().toISOString().slice(0, 10)
} = {}) {
    const changesDir = path.join(rootDir, 'changes');
    const changes = loadChangeFragments(changesDir);
    if (!changes.length) {
        throw new Error('Žádné change fragmenty k vydání nebyly nalezeny.');
    }

    const packageJson = readJson(path.join(rootDir, 'package.json'));
    const selectedType = determineReleaseType(changes, releaseType);
    const version = bumpVersion(packageJson.version, selectedType);
    const sections = groupChanges(changes);
    const releaseNotes = {
        version,
        date,
        summary: buildSummary(version, sections),
        sections
    };

    updateVersionFiles(rootDir, version);
    writeJson(path.join(rootDir, 'release-notes.json'), releaseNotes);

    const changelogPath = path.join(rootDir, 'CHANGELOG.md');
    const changelog = fs.readFileSync(changelogPath, 'utf8');
    const entry = renderChangelogEntry(version, date, sections);
    fs.writeFileSync(changelogPath, prependChangelog(changelog, entry), 'utf8');

    for (const change of changes) {
        fs.unlinkSync(change.filePath);
    }

    return {
        version,
        releaseType: selectedType,
        changeCount: changes.length,
        releaseNotesPath: path.join(rootDir, 'release-notes.json')
    };
}

function parseCliArgs(args) {
    let releaseType = null;
    for (let index = 0; index < args.length; index += 1) {
        if (args[index] === '--type') {
            releaseType = args[index + 1];
            index += 1;
        }
    }
    return { releaseType };
}

if (require.main === module) {
    try {
        const options = parseCliArgs(process.argv.slice(2));
        const result = prepareRelease(options);
        console.log(`Připraveno vydání ${result.version} (${result.releaseType}).`);
        console.log(`Zpracováno změn: ${result.changeCount}.`);
        console.log('Zkontrolujte diff, spusťte testy a vytvořte release commit.');
    } catch (error) {
        console.error(`Release nebyl připraven: ${error.message}`);
        process.exit(1);
    }
}

module.exports = {
    bumpVersion,
    determineReleaseType,
    groupChanges,
    prepareRelease,
    renderChangelogEntry
};
