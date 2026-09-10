param(
    [string]$ModVersion = "1.8.4"
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem

$RepoRoot = Split-Path $PSScriptRoot -Parent
$SrcDir = Join-Path $RepoRoot "src"
$ImagesDir = Join-Path $RepoRoot "images"
$BinDir = Join-Path $PSScriptRoot "bin"
$ResDir = Join-Path $BinDir "res"
$ModsDir = Join-Path $ResDir "scripts\client\gui\mods"
$GuiAssetsDir = Join-Path $ResDir "gui\pademinune"
$OutDir = Join-Path $BinDir "wotmods"
$ModName = "pademinune-armor-calculator-$ModVersion"
$OutFile = Join-Path $OutDir "$ModName.wotmod"

$Modules = @(
    "mod_armor_pen_calculator.py",
    "pade_constants.py",
    "pade_gui.py",
    "pade_config.py",
    "mod_pade_settings_gui.py",
    "pade_track.py"
)

# Always stage from a clean res tree so removed/renamed modules cannot leak
# into a new .wotmod from an older build.
if (Test-Path $ResDir) {
    Remove-Item -Recurse -Force $ResDir
}

New-Item -ItemType Directory -Force -Path $ModsDir | Out-Null
New-Item -ItemType Directory -Force -Path $GuiAssetsDir | Out-Null
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

# Compile exactly the modules that the mod loads.
foreach ($Module in $Modules) {
    $Source = Join-Path $SrcDir $Module
    python27 -m py_compile $Source
    if ($LASTEXITCODE -ne 0) {
        throw "Python 2.7 compilation failed for $Module"
    }

    $Pyc = "$Source" + "c"
    Copy-Item -Force $Pyc (Join-Path $ModsDir ([System.IO.Path]::GetFileName($Pyc)))
    Remove-Item -Force $Pyc
}

# Track indicator assets used by pade_track.py.
$TrackAssets = @(
    "crosshair-32-green.png",
    "crosshair-32-orange.png"
)
foreach ($Asset in $TrackAssets) {
    $SourceAsset = Join-Path $ImagesDir $Asset
    if (-not (Test-Path $SourceAsset)) {
        throw "Missing required GUI asset: $SourceAsset"
    }
    Copy-Item -Force $SourceAsset (Join-Path $GuiAssetsDir $Asset)
}

if (Test-Path $OutFile) {
    Remove-Item -Force $OutFile
}

# .wotmod is a ZIP whose root contains res\...
[System.IO.Compression.ZipFile]::CreateFromDirectory(
    $ResDir,
    $OutFile,
    [System.IO.Compression.CompressionLevel]::NoCompression,
    $true
)

Write-Output "Packaged: $OutFile"
