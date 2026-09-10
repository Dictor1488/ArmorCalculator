param(
    [string]$ModVersion = "1.8.4"
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem

$RepoRoot = Split-Path $PSScriptRoot -Parent
$SrcDir = Join-Path $RepoRoot "src"
$BinDir = Join-Path $PSScriptRoot "bin"
$ResDir = Join-Path $BinDir "res"
$ModsDir = Join-Path $ResDir "scripts\client\gui\mods"
$OutDir = Join-Path $BinDir "wotmods"
$ModName = "unicorn.ares-armor-calculator-$ModVersion"
$OutFile = Join-Path $OutDir "$ModName.wotmod"

$Modules = @(
    "mod_armor_pen_calculator.py",
    "pade_constants.py",
    "pade_gui.py",
    "pade_config.py",
    "mod_pade_settings_gui.py"
)

if (Test-Path $ResDir) {
    Remove-Item -Recurse -Force $ResDir
}

New-Item -ItemType Directory -Force -Path $ModsDir | Out-Null
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

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

if (Test-Path $OutFile) {
    Remove-Item -Force $OutFile
}

[System.IO.Compression.ZipFile]::CreateFromDirectory(
    $ResDir,
    $OutFile,
    [System.IO.Compression.CompressionLevel]::NoCompression,
    $true
)

Write-Output "Packaged: $OutFile"
