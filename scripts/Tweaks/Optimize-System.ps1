
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-Log "Applying System Optimizations..."

# 1. Disable Hibernation (Saves disk space) and Fast Startup
try {
    powercfg -h off
    reg.exe add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f
    Write-Log "Hibernation and Fast Startup disabled."
} catch {
    Write-Log "Failed to disable hibernation and Fast Startup: $_"
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

# 5. Disable App Launch Tracking
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\EdgeUI" /v DisableMFUTracking /t REG_DWORD /d 1 /f
reg.exe add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v NoInstrumentation /t REG_DWORD /d 1 /f

Write-Log "System Optimizations Applied."
