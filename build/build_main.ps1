param(
    [string]$GameRoot = "C:\\Games\\World_of_Tanks_EU",
    [string]$GameVersion = "2.4.0.5429"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
$SrcDir = Join-Path $RepoRoot "src"
$GamefaceDir = Join-Path $RepoRoot "gameface"
$BinDir = Join-Path $PSScriptRoot "bin"
$ResModsRoot = Join-Path $GameRoot ("res_mods\\{0}" -f $GameVersion)
$ModsDest = Join-Path $ResModsRoot "scripts\client\gui\mods"
$GamefaceDest = Join-Path $ResModsRoot "gui\gameface\mods\unicorn_ares\ArmorCalculator"
$ResMapDest = Join-Path $ResModsRoot "mods\configs\res_map"

$Modules = @(
    "mod_unicorn_ares_armor.py",
    "mod_unicorn_ares_settings.py",
    "unicorn_ares_config.py",
    "unicorn_ares_constants.py",
    "unicorn_ares_gui.py"
)

New-Item -ItemType Directory -Force -Path $BinDir, $ModsDest, $GamefaceDest, $ResMapDest | Out-Null

foreach ($Module in $Modules) {
    $Source = Join-Path $SrcDir $Module
    python27 -m py_compile $Source
    if ($LASTEXITCODE -ne 0) {
        throw "Python 2.7 compilation failed for $Module"
    }
    $Pyc = "$Source" + "c"
    $TargetPyc = Join-Path $BinDir ([System.IO.Path]::GetFileName($Pyc))
    Move-Item -Force $Pyc $TargetPyc
    Copy-Item -Force $TargetPyc $ModsDest
}

Copy-Item -Force (Join-Path $GamefaceDir "ArmorCalculatorBattle.html") $GamefaceDest
Copy-Item -Force (Join-Path $GamefaceDir "ArmorCalculator.css") $GamefaceDest
Copy-Item -Force (Join-Path $GamefaceDir "ArmorCalculator.js") $GamefaceDest
Copy-Item -Force (Join-Path $GamefaceDir "armor_calculator_res_map.json") (Join-Path $ResMapDest "armor_calculator_gameface.json")

Write-Output "Compiled and copied unicorn.ares Armor Calculator GameFace files to '$ResModsRoot'"
