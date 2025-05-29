const { FusesPlugin } = require('@electron-forge/plugin-fuses');
const { FuseV1Options, FuseVersion } = require('@electron/fuses');

module.exports = {
  packagerConfig: {
    name: 'NastrojeOPJAK',
    // icon: './src/electron/assets/icon',
    asar: {
      unpack: '{*.{node,dll,exe,so,dylib},src/python/**/*}'
    },
    extraResource: [
      './resources/python-dist'
    ],
    ignore: [
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
      /\.bat$/
    ]
  },
  rebuildConfig: {},
  makers: [
    {
      name: '@electron-forge/maker-zip',
      platforms: ['win32', 'darwin', 'linux'],
    },
    // {
    //   name: '@electron-forge/maker-squirrel',
    //   config: {
    //     name: 'NastrojeOPJAK',
    //     authors: 'Max Parez',
    //     description: 'Nástroje pro ŠI a ŠII OP JAK',
    //     // setupIcon: './src/electron/assets/icon.ico',
    //     setupExe: 'NastrojeOPJAK-Setup.exe',
    //     noMsi: true
    //   },
    // },
    {
      name: '@electron-forge/maker-deb',
      config: {
        options: {
          maintainer: 'Max Parez',
          homepage: 'https://github.com/maxparez/electron_app'
        }
      },
    },
    {
      name: '@electron-forge/maker-rpm',
      config: {},
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
