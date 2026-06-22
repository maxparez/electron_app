const path = require('path');

const FILTERS = {
    pdf: { name: 'PDF Files', extensions: ['pdf'] },
    xlsx: { name: 'Excel Files', extensions: ['xlsx'] },
    xls: { name: 'Excel Files', extensions: ['xls', 'xlsx'] },
    csv: { name: 'CSV Files', extensions: ['csv'] },
    tsv: { name: 'TSV Files', extensions: ['tsv', 'txt'] }
};

const ALL_FILES_FILTER = { name: 'All Files', extensions: ['*'] };

function uniqueFilters(filters) {
    const seen = new Set();
    return filters.filter((filter) => {
        const key = `${filter.name}:${filter.extensions.join(',')}`;
        if (seen.has(key)) {
            return false;
        }
        seen.add(key);
        return true;
    });
}

function buildSaveDialogOptions(defaultName, options = {}) {
    const extension = path.extname(defaultName || '').replace('.', '').toLowerCase();
    const preferredFilter = FILTERS[extension] || null;
    const fallbackFilters = [
        FILTERS.xlsx,
        FILTERS.csv,
        FILTERS.tsv,
        FILTERS.pdf,
        ALL_FILES_FILTER
    ];

    return {
        ...options,
        defaultPath: options.defaultPath || defaultName,
        filters: options.filters || uniqueFilters([
            ...(preferredFilter ? [preferredFilter] : []),
            ...fallbackFilters
        ])
    };
}

module.exports = {
    buildSaveDialogOptions
};
