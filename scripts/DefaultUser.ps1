
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-Log "Configuring Default User..."

# Load Default User Hive
$defaultUserHive = "HKU\DefaultUser"

# Robustly load hive: Check if already loaded first
if (-not (Test-Path "Registry::$defaultUserHive")) {
    Write-Log "Loading Default User hive..."
    reg.exe load $defaultUserHive "C:\Users\Default\NTUSER.DAT"
} else {
    Write-Log "Default User hive already loaded."
}

try {
    # Taskbar and Explorer settings
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v ShowTaskViewButton /t REG_DWORD /d 0 /f
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarAl /t REG_DWORD /d 0 /f # Left align taskbar
    reg.exe add "$defaultUserHive\Software\Policies\Microsoft\Windows\Explorer" /v DisableSearchBoxSuggestions /t REG_DWORD /d 1 /f

    # NEW: Launch Explorer to "This PC" (1)
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v LaunchTo /t REG_DWORD /d 1 /f

    # NEW: Search Icon only on Taskbar (3)
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Search" /v SearchboxTaskbarMode /t REG_DWORD /d 3 /f

    # Show File Extensions
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v HideFileExt /t REG_DWORD /d 0 /f

    # Show "This PC" Icon on Desktop
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel" /v "{20D04FE0-3AEA-1069-A2D8-08002B30309D}" /t REG_DWORD /d 0 /f

    # Enable Dark Mode (System and Apps)
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 0 /f
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 0 /f

    # Classic Context Menu (Windows 11)
    reg.exe add "$defaultUserHive\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /ve /t REG_SZ /d "" /f

    # Disable Lock Screen Tips
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v RotatingLockScreenEnabled /t REG_DWORD /d 0 /f
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SubscribedContent-338387Enabled /t REG_DWORD /d 0 /f

    # NEW: Disable "Finish setting up your device"
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\UserProfileEngagement" /v ScoobeSystemSettingEnabled /t REG_DWORD /d 0 /f

    # Disable Copilot for Default User
    reg.exe add "$defaultUserHive\Software\Policies\Microsoft\Windows\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f

    # Enable End Task in Taskbar (Developer/Power User feature)
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarEndTask /t REG_DWORD /d 1 /f

    # Run UserOnce on first login
    # Use cmd /c if exist to avoid errors if scripts are deleted by previous user
    $cmd = "cmd.exe /c if exist `"C:\Windows\Setup\Scripts\UserOnce.ps1`" powershell.exe -WindowStyle Hidden -ExecutionPolicy Unrestricted -NoProfile -File `"C:\Windows\Setup\Scripts\UserOnce.ps1`""
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\RunOnce" /v "UnattendedSetup" /t REG_SZ /d $cmd /f
}
finally {
    # Only unload if we are sure we are done.
    # But since we are the only ones touching it in this scope, we should unload.
    Write-Log "Unloading Default User hive..."
    reg.exe unload $defaultUserHive
    [GC]::Collect()
}

Write-Log "Default User Configuration Completed."
