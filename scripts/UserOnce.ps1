
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-Log "Configuring User Account..."

# Disable Copilot (Ensure it's removed for the user)
Get-AppxPackage -Name 'Microsoft.Windows.Ai.Copilot.Provider' | Remove-AppxPackage -ErrorAction SilentlyContinue

# Register Daily Winget Auto-Update Task (Transparent)
# Registers a per-user task to update software
$taskName = "DailySoftwareUpdate-$env:USERNAME"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -Command `\"winget source update; winget upgrade --all --include-unknown --silent --disable-interactivity --accept-source-agreements --accept-package-agreements`\""
$trigger = New-ScheduledTaskTrigger -Daily -At 13:00
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -Hidden -RunOnlyIfNetworkAvailable
Register-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -TaskName $taskName -Description "Automatically updates all software via Winget silently." -RunLevel Highest -Force | Out-Null
Write-Log "Registered Daily Winget Auto-Update Task: $taskName"

Write-Log "User Configuration Completed."

# Self-Destruct: Cleanup Scripts
# Wait 5 seconds then delete the script folder
Start-Process -FilePath "cmd.exe" -ArgumentList "/c timeout /t 5 /nobreak > NUL & rmdir /s /q `"$env:SystemRoot\Setup\Scripts`"" -WindowStyle Hidden
