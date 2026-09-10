param(
    [string]$GameRoot = "C:\\Games\\World_of_Tanks_EU",
    [string]$GameVersion = "2.4.0.5429"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
$SrcDir = Join-Path $RepoRoot "src"
$BinDir = Join-Path $PSScriptRoot "bin"
$Dest = Join-Path $GameRoot ("res_mods\\{0}\\scripts\\client\\gui\\mods" -f $GameVersion)

$Modules = @(
    "mod_armor_pen_calculator.py",
    "pade_constants.py",
    "pade_gui.py",
    "pade_config.py",
    "mod_pade_settings_gui.py",
    "pade_track.py"
)

New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
New-Item -ItemType Directory -Force -Path $Dest | Out-Null

foreach ($Module in $Modules) {
    $Source = Join-Path $SrcDir $Module
    python27 -m py_compile $Source
    if ($LASTEXITCODE -ne 0) {
        throw "Python 2.7 compilation failed for $Module"
    }

    $Pyc = "$Source" + "c"
    $TargetPyc = Join-Path $BinDir ([System.IO.Path]::GetFileName($Pyc))
    Move-Item -Force $Pyc $TargetPyc
    Copy-Item -Force $TargetPyc $Dest
}

Write-Output "Compiled and copied mod files to '$Dest'"
