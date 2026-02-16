$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-Log "Configuring User Account..."

# Disable Copilot (Appx)
try {
    $copilot = Get-AppxPackage -Name 'Microsoft.Windows.Ai.Copilot.Provider' -ErrorAction SilentlyContinue
    if ($copilot) {
        $copilot | Remove-AppxPackage -ErrorAction SilentlyContinue
        Write-Log "Copilot Appx removed."
    }
} catch {
    Write-Log "Failed to remove Copilot Appx: $_"
}

# Explorer Settings
$explorerKey = 'Registry::HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
if (-not (Test-Path $explorerKey)) { New-Item -Path $explorerKey -Force | Out-Null }
Set-ItemProperty -LiteralPath $explorerKey -Name 'LaunchTo' -Type 'DWord' -Value 1 -Force
Set-ItemProperty -LiteralPath $explorerKey -Name 'TaskbarAl' -Type 'DWord' -Value 0 -Force # Align Left

$searchKey = 'Registry::HKCU\Software\Microsoft\Windows\CurrentVersion\Search'
if (-not (Test-Path $searchKey)) { New-Item -Path $searchKey -Force | Out-Null }
Set-ItemProperty -LiteralPath $searchKey -Name 'SearchboxTaskbarMode' -Type 'DWord' -Value 3 -Force # Icon only

# Disable "Finish setting up your device"
$scoobeKey = 'Registry::HKCU\Software\Microsoft\Windows\CurrentVersion\UserProfileEngagement'
if (-not (Test-Path $scoobeKey)) { New-Item -Path $scoobeKey -Force | Out-Null }
Set-ItemProperty -LiteralPath $scoobeKey -Name 'ScoobeSystemSettingEnabled' -Type 'DWord' -Value 0 -Force -ErrorAction SilentlyContinue

# Disable Lock Screen Tips
$contentKey = 'Registry::HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager'
if (-not (Test-Path $contentKey)) { New-Item -Path $contentKey -Force | Out-Null }
Set-ItemProperty -LiteralPath $contentKey -Name 'SubscribedContent-338387Enabled' -Type 'DWord' -Value 0 -Force -ErrorAction SilentlyContinue

# Restart Explorer to apply changes
Get-Process -Name 'explorer' -ErrorAction 'SilentlyContinue' | Stop-Process -Force

# Register Daily Winget Auto-Update Task (Transparent)
$taskName = "DailySoftwareUpdate"
$wingetCmd = "winget source update; winget upgrade --all --include-unknown --silent --disable-interactivity --accept-source-agreements --accept-package-agreements"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -Command `\"$wingetCmd`\""
$trigger = New-ScheduledTaskTrigger -Daily -At 13:00
# Attempt 1: Try with Highest RunLevel (Admin)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -Hidden -RunOnlyIfNetworkAvailable

$registered = $false
try {
    Write-Log "Attempting to register Winget task with Highest privileges..."
    Register-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -TaskName $taskName -Description "Automatically updates all software via Winget silently." -RunLevel Highest -Force -ErrorAction Stop | Out-Null
    $registered = $true
    Write-Log "Registered Daily Winget Auto-Update Task (Highest)."
} catch {
    Write-Log "Failed to register Winget task with Highest privileges: $_"
}

# Attempt 2: Try with Limited (User) privileges if Admin failed (e.g., UAC issue)
if (-not $registered) {
    try {
        Write-Log "Attempting to register Winget task with Limited privileges..."
        Register-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -TaskName $taskName -Description "Automatically updates all software via Winget silently." -RunLevel Limited -Force -ErrorAction Stop | Out-Null
        $registered = $true
        Write-Log "Registered Daily Winget Auto-Update Task (Limited)."
    } catch {
        Write-Log "Failed to register Winget task (Limited): $_"
    }
}

Write-Log "User Configuration Completed."

# Self-Destruct: Cleanup Scripts
# Wait 5 seconds then delete the script folder
Start-Process -FilePath "cmd.exe" -ArgumentList "/c timeout /t 5 /nobreak > NUL & rmdir /s /q `"$env:SystemRoot\Setup\Scripts`"" -WindowStyle Hidden
