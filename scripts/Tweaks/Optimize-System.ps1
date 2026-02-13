
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\..\Lib\Helper.ps1"

Write-Log "Applying System Optimizations..."

# 1. Disable Hibernation (Saves disk space)
try {
    powercfg -h off
    Write-Log "Hibernation disabled."
} catch {
    Write-Log "Failed to disable hibernation: $_"
}

# 2. Set High Performance Power Plan
try {
    powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
    Write-Log "Power plan set to High Performance."
} catch {
    Write-Log "Failed to set power plan: $_"
}

# 3. Disable Game DVR (Background recording)
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /v AllowGameDVR /t REG_DWORD /d 0 /f

# 4. Disable Last Access Timestamp (Reduces disk I/O)
try {
    fsutil behavior set disablelastaccess 1
    Write-Log "Last Access Timestamp disabled."
} catch {
    Write-Log "Failed to disable Last Access Timestamp: $_"
}

Write-Log "System Optimizations Applied."
