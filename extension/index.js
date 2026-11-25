/*
 * Vortex game extension: Obenseuer
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * - Game ID matches the Nexus Mods domain, which is spelled "obeseuer"
 *   (https://www.nexusmods.com/obeseuer). This is what lets Vortex link
 *   downloads, update checks and Collections to the right Nexus game.
 * - Obenseuer is a Unity (Mono) game; its mods are BepInEx plugins.
 *   BepInEx handling is delegated to Vortex's bundled "modtype-bepinex"
 *   extension (injector / plugins / patchers / root mod types).
 * - BepInEx is pinned to 5.4.23.6 and fetched from the official BepInEx
 *   GitHub releases when missing, so collection users get it automatically.
 */
const path = require('path');
const { fs, util } = require('vortex-api');

const GAME_ID = 'obeseuer';
const GAME_NAME = 'Obenseuer';
const STEAMAPP_ID = '951240';
const EXE_NAME = 'Obenseuer.exe';
const BEPINEX_VERSION = '5.4.23.6';

function findGame() {
  return util.GameStoreHelper.findByAppId([STEAMAPP_ID]).then((game) => game.gamePath);
}

function requiresLauncher(gamePath, store) {
  // Let Steam start the game so Steam overlay / achievements / cloud saves work.
  if (store === 'steam' || store === undefined) {
    return Promise.resolve({ launcher: 'steam' });
  }
  return Promise.resolve(undefined);
}

function prepareForModding(discovery) {
  return fs.ensureDirWritableAsync(path.join(discovery.path, 'BepInEx', 'plugins'));
}

// ---------------------------------------------------------------------------
// Installer for archives that ship a "BepInEx/..." folder, optionally wrapped
// in a top-level folder (e.g. "MyMod-1.0/BepInEx/plugins/MyMod.dll").
// Vortex's bundled BepInEx installers only recognise archives whose first
// folder is plugins/config/patchers, so without this the files would end up
// at BepInEx/plugins/BepInEx/plugins/...
// Full BepInEx packs (the loader itself) are caught earlier by the bundled
// injector installer (priority 10), so they never reach this one.
// ---------------------------------------------------------------------------
const BEPINEX_DIR = 'bepinex';

function bepinexSegmentIndex(filePath) {
  return filePath.split(path.sep).findIndex((seg) => seg.toLowerCase() === BEPINEX_DIR);
}

function isFile(filePath) {
  return !filePath.endsWith(path.sep);
}

function testBepInExFolderMod(files, gameId) {
  const supported =
    gameId === GAME_ID &&
    files.some((file) => {
      const idx = bepinexSegmentIndex(file);
      // Needs at least one file *inside* the BepInEx folder.
      return isFile(file) && idx !== -1 && idx < file.split(path.sep).length - 1;
    });
  return Promise.resolve({ supported, requiredFiles: [] });
}

function installBepInExFolderMod(files) {
  const instructions = files
    .filter(isFile)
    .map((file) => {
      const segments = file.split(path.sep);
      const idx = bepinexSegmentIndex(file);
      if (idx === -1) {
        // Readmes etc. that sit outside the BepInEx folder are skipped.
        return undefined;
      }
      return {
        type: 'copy',
        source: file,
        destination: segments.slice(idx + 1).join(path.sep),
      };
    })
    .filter((instr) => instr !== undefined);

  // "bepinex-root" deploys relative to <game>/BepInEx.
  instructions.push({ type: 'setmodtype', value: 'bepinex-root' });
  return Promise.resolve({ instructions });
}

function main(context) {
  context.requireExtension('modtype-bepinex');

  context.registerGame({
    id: GAME_ID,
    name: GAME_NAME,
    mergeMods: true,
    queryPath: findGame,
    queryModPath: () => path.join('BepInEx', 'plugins'),
    logo: 'gameart.png',
    executable: () => EXE_NAME,
    requiredFiles: [EXE_NAME, 'UnityPlayer.dll'],
    setup: prepareForModding,
    requiresLauncher,
    environment: {
      SteamAPPId: STEAMAPP_ID,
    },
    details: {
      steamAppId: +STEAMAPP_ID,
      nexusPageId: GAME_ID,
    },
  });

  context.registerInstaller('obeseuer-bepinex-folder', 25, testBepInExFolderMod, installBepInExFolderMod);

  context.once(() => {
    if (context.api.ext.bepinexAddGame !== undefined) {
      context.api.ext.bepinexAddGame({
        gameId: GAME_ID,
        // Pinned to BepInEx 5.4.23.6 (Unity Mono, win x64). If no BepInEx is
        // installed yet, Vortex offers to download
        // BepInEx_win_x64_5.4.23.6.zip from the official GitHub releases.
        // Installing that same zip manually works too; Vortex then skips the download.
        bepinexVersion: BEPINEX_VERSION,
        architecture: 'x64',
        autoDownloadBepInEx: true,
        forceGithubDownload: true,
      });
    }
  });

  return true;
}

module.exports = {
  default: main,
};
