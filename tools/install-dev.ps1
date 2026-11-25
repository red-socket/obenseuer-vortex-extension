# Copies the extension into Vortex's user plugins folder for local testing.
# Restart Vortex afterwards so it loads the new code.
#
# Remove this dev copy (or run with -Uninstall) before installing the
# published extension from Nexus Mods, so Vortex doesn't load two
# extensions for the same game.
param(
    [switch]$Uninstall
)

$ErrorActionPreference = 'Stop'
$source = Join-Path $PSScriptRoot '..\extension'
$target = Join-Path $env:APPDATA 'Vortex\plugins\game-obeseuer'

if ($Uninstall) {
    if (Test-Path $target) {
        Remove-Item $target -Recurse -Force
        Write-Host "Removed $target. Restart Vortex."
    } else {
        Write-Host "Nothing to remove at $target."
    }
    return
}

New-Item -ItemType Directory -Force $target | Out-Null
# Clear old files first so renamed or deleted files don't linger.
Get-ChildItem $target -Force | Remove-Item -Recurse -Force
Copy-Item (Join-Path $source '*') $target -Recurse -Force
Write-Host "Installed to $target. Restart Vortex to load it."
