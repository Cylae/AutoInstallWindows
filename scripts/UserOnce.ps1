$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-Log "Configuring User Account..."

# Cleanup Copilot (Per-User)
try {
    Write-Log "Attempting per-user Copilot cleanup..."
    Get-AppxPackage -Name "*Copilot*" -ErrorAction Stop | Remove-AppxPackage -ErrorAction Stop
    Write-Log "Copilot app removed for current user."
} catch {
    Write-Log "Copilot not found or error removing for current user: $_"
}

# Register Daily Winget Auto-Update Task (Transparent)
if (Get-Command winget -ErrorAction SilentlyContinue) {
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
} else {
    Write-Log "Winget not found. Skipping auto-update task registration."
}

Write-Log "User Configuration Completed."

# Self-Destruct: Cleanup Scripts
# Wait 10 seconds then delete the script folder
Start-Process -FilePath "cmd.exe" -ArgumentList "/c timeout /t 10 /nobreak > NUL & rmdir /s /q `"$env:SystemRoot\Setup\Scripts`"" -WindowStyle Hidden
