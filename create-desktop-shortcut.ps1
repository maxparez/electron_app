# PowerShell script pro vytvoření zástupce na ploše

$WshShell = New-Object -comObject WScript.Shell
$Desktop = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = "$Desktop\Nástroje OP JAK.lnk"

# Vytvoř zástupce
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "$PSScriptRoot\start-app.bat"
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.IconLocation = "$PSScriptRoot\src\electron\assets\icon.ico"
$Shortcut.Description = "Nástroje pro zpracování dokumentace OP JAK"
$Shortcut.Save()

Write-Host "✅ Zástupce vytvořen na ploše" -ForegroundColor Green