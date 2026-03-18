$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-Log "Configuring User Account..."

# Register Daily Winget Auto-Update Task (Transparent)
$taskName = "DailySoftwareUpdate"
$wingetCmd = "winget source update; winget upgrade --all --include-unknown --silent --disable-interactivity --accept-source-agreements --accept-package-agreements"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -Command `"$wingetCmd`""
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

# Cleanup remaining packages that might have reappeared or weren't cleaned
try { Get-AppxPackage -Name "Microsoft.Windows.Ai.Copilot.Provider" -AllUsers | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue } catch {}
$copilotKey = "HKCU\Software\Policies\Microsoft\Windows\WindowsCopilot"
if (-not (Test-Path $copilotKey)) { New-Item -Path $copilotKey -Force | Out-Null }
Set-ItemProperty -Path $copilotKey -Name "TurnOffWindowsCopilot" -Value 1 -Type DWord -Force

Write-Log "User Configuration Completed."

# Self-Destruct: Cleanup Scripts
# Wait 10 seconds then delete the script folder
Start-Process -FilePath "cmd.exe" -ArgumentList "/c timeout /t 10 /nobreak > NUL & rmdir /s /q `"$env:SystemRoot\Setup\Scripts`"" -WindowStyle Hidden
