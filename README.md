# Obenseuer Vortex extension

Adds [Obenseuer](https://store.steampowered.com/app/951240/Obenseuer/) support to
[Vortex](https://www.nexusmods.com/about/vortex/), the Nexus Mods mod manager,
so Obenseuer mods can be installed, managed and shared as Collections.

## What it does

- Finds the Steam install (app 951240) and launches the game through Steam.
- Sets up BepInEx through Vortex's bundled BepInEx support. If BepInEx is not
  installed, Vortex offers to download **BepInEx 5.4.23.6** (win x64) from the
  official [BepInEx releases](https://github.com/BepInEx/BepInEx/releases).
- Deploys plugin DLLs to `BepInEx/plugins`.
- Handles mod archives that contain a `BepInEx/...` folder, so files land in
  the right place instead of `BepInEx/plugins/BepInEx/plugins/...`.

The Vortex game ID is `obeseuer` to match the Nexus Mods domain
(nexusmods.com/obeseuer), which is spelled that way on Nexus. The Nexus
numeric game ID is `6792`.

## Repository layout

| Path | Contents |
| --- | --- |
| `extension/` | Exactly what goes in the release archive: `index.js`, `info.json`, `gameart.png` |
| `tools/package.py` | Validates the extension and builds `dist/obenseuer-vortex-extension-<version>.zip` |
| `tools/install-dev.ps1` | Copies `extension/` into Vortex for local testing |

## Developing

Vortex runs on Windows. To test changes:

```powershell
powershell -ExecutionPolicy Bypass -File tools/install-dev.ps1
```

Then restart Vortex. Vortex's log is at `%APPDATA%\Vortex\vortex.log`; search
it for `obeseuer`.

Before installing the published extension from Nexus Mods, remove the dev copy
so Vortex doesn't load two extensions for the same game:

```powershell
powershell -ExecutionPolicy Bypass -File tools/install-dev.ps1 -Uninstall
```

## Releasing

1. Bump `version` in `extension/info.json` (Semantic Versioning) and add a
   matching `## [x.y.z]` entry to `CHANGELOG.md`.
2. Build the archive:

   ```sh
   python3 -I tools/package.py
   ```

   It refuses to build if the archive would break Nexus's packaging rules
   (missing fields, byte-order mark in `info.json`, wrong art size, and so on).
3. Tag the commit `v<version>` and push the tag.
4. Upload `dist/obenseuer-vortex-extension-<version>.zip` on Nexus Mods:
   **Upload → Upload mod**, Game **Modding Tools**, Category
   **Vortex Extensions**, as the single file under **Main Files**, with the
   same version as `info.json`. Updates go on the same page.

Vortex picks up new extensions and updates within about two hours. Nexus
reviews extensions periodically after they go live. See Nexus's
[packaging guide](https://github.com/Nexus-Mods/Vortex/wiki/How-to-package-a-game-extension)
and [upload guide](https://github.com/Nexus-Mods/Vortex/wiki/How-to-upload-an-extension-to-nexus).

## License

[GPL-3.0-or-later](LICENSE).
