
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-SetupLog "Applying System Optimizations..."

# 1. Disable Hibernation (Saves disk space)
try {
    powercfg -h off
    Write-SetupLog "Hibernation disabled."
} catch {
    Write-SetupLog "Failed to disable hibernation: $_"
}

# 2. Set High Performance Power Plan
try {
    powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
    Write-SetupLog "Power plan set to High Performance."
} catch {
    Write-SetupLog "Failed to set power plan: $_"
}

# 3. Disable Game DVR (Background recording)
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" -Name "AllowGameDVR" -Value "0" -Type "REG_DWORD"

# 4. Disable Last Access Timestamp (Reduces disk I/O)
try {
    fsutil behavior set disablelastaccess 1
    Write-SetupLog "Last Access Timestamp disabled."
} catch {
    Write-SetupLog "Failed to disable Last Access Timestamp: $_"
}

# 5. Disable App Launch Tracking
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\EdgeUI" -Name "DisableMFUTracking" -Value "1" -Type "REG_DWORD"
Set-RegistryKey -Path "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" -Name "NoInstrumentation" -Value "1" -Type "REG_DWORD"

Write-SetupLog "System Optimizations Applied."
