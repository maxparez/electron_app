const { FusesPlugin } = require('@electron-forge/plugin-fuses');
const { FuseV1Options, FuseVersion } = require('@electron/fuses');

module.exports = {
  packagerConfig: {
    name: 'ElektronApp',
    productName: 'ElektronApp - Nástroje OP JAK',
    icon: './src/electron/assets/icon',
    asar: {
      unpack: '{*.{node,dll,exe,so,dylib},src/python/**/*,src/launcher.js}'
    },
    extraResource: [
      './src/python',
      './requirements.txt',
      './python-backend-install.bat'
    ],
    ignore: [
      /electron-app-env/,
      /venv/,
      /logs/,
      /out/,
      /\.git/,
      /\.pytest_cache/,
      /test_/,
      /legacy_code/,
      /_context_notes\.md/,
      /PLAKAT_PROGRESS\.md/,
      /PROGRESS\.md/,
      /PROJECT_PLAN\.md/,
      /TESTING_PLAN\.md/,
      /debug_/,
      /inspect_/,
      /simple_test\.py/,
      /test_complete/,
      /ui_preview/,
      /\.sh$/,
      /template_.*\.xlsx$/,
      /standalone-backend\.py$/,
      /start-.*\.bat$/,
      /test-.*\.bat$/,
      /quick-fix-.*\.bat$/,
      /debug-.*\.bat$/,
      /build-.*\.bat$/,
      /next-tag\.sh$/,
      /install_mcp_servers\.sh$/
    ]
  },
  rebuildConfig: {},
  makers: [
    {
      name: '@electron-forge/maker-squirrel',
      platforms: ['win32'],
      config: {
        name: 'ElektronApp',
        authors: 'Max Parez',
        description: 'ElektronApp - Nástroje pro zpracování projektové dokumentace OP JAK',
        setupExe: 'ElektronApp-Setup.exe',
        noMsi: true,
        remoteReleases: false,
        createDesktopShortcut: true,
        createStartMenuShortcut: true
      },
    },
  ],
  plugins: [
    {
      name: '@electron-forge/plugin-auto-unpack-natives',
      config: {},
    },
    // Fuses are used to enable/disable various Electron functionality
    // at package time, before code signing the application
    new FusesPlugin({
      version: FuseVersion.V1,
      [FuseV1Options.RunAsNode]: false,
      [FuseV1Options.EnableCookieEncryption]: true,
      [FuseV1Options.EnableNodeOptionsEnvironmentVariable]: false,
      [FuseV1Options.EnableNodeCliInspectArguments]: false,
      [FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true,
      [FuseV1Options.OnlyLoadAppFromAsar]: true,
    }),
  ],
};
