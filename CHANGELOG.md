# Changelog

All notable changes to this extension are documented here.
Versions follow [Semantic Versioning](https://semver.org/) and match the version on Nexus Mods.

## [0.1.0] - Unreleased

### Added
- Steam discovery for Obenseuer (app 951240); the game launches through Steam.
- BepInEx support through Vortex's bundled BepInEx extension. If BepInEx is missing,
  Vortex offers to download BepInEx 5.4.23.6 (win x64) from the official GitHub releases.
- Plugin DLLs deploy to `BepInEx/plugins`.
- Installer for archives that ship a `BepInEx/...` folder (optionally inside a
  wrapper folder), so they deploy relative to the game's `BepInEx` folder.
