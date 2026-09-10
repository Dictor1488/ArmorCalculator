param(
    [string]$GameRoot = "C:\\Games\\World_of_Tanks_EU",
    [string]$GameVersion = "2.4.0.5429"
)

$ResModsRoot = Join-Path $GameRoot ("res_mods\\{0}" -f $GameVersion)
$ModsDest = Join-Path $ResModsRoot "scripts\client\gui\mods"

$Files = @(
    "mod_unicorn_ares_armor.pyc",
    "mod_unicorn_ares_settings.pyc",
    "unicorn_ares_config.pyc",
    "unicorn_ares_constants.pyc",
    "unicorn_ares_gui.pyc"
)
foreach ($File in $Files) {
    Remove-Item (Join-Path $ModsDest $File) -Force -ErrorAction SilentlyContinue
}

Remove-Item (Join-Path $ResModsRoot "gui\gameface\mods\unicorn_ares\ArmorCalculator") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $ResModsRoot "mods\configs\res_map\armor_calculator_gameface.json") -Force -ErrorAction SilentlyContinue

Write-Output "Removed unicorn.ares Armor Calculator from '$ResModsRoot'"
