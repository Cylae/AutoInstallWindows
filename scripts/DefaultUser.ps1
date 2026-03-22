
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-Log "Configuring Default User..."

# Load Default User Hive
$defaultUserHive = "HKU\DefaultUser"
$weLoadedIt = $false

# Robustly load hive: Check if already loaded first
if (-not (Test-Path "Registry::$defaultUserHive")) {
    Write-Log "Loading Default User hive..."
    try {
        $result = reg.exe load $defaultUserHive "C:\Users\Default\NTUSER.DAT" 2>&1
        if ($LASTEXITCODE -eq 0) {
            $weLoadedIt = $true
        } else {
            Write-Log "Failed to load Default User hive: $result"
            return
        }
    } catch {
        Write-Log "Exception loading Default User hive: $_"
        return
    }
} else {
    Write-Log "Default User hive already loaded."
}

try {
    # Taskbar and Explorer settings
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v ShowTaskViewButton /t REG_DWORD /d 0 /f
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarAl /t REG_DWORD /d 0 /f # Left align taskbar
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v LaunchTo /t REG_DWORD /d 1 /f # Open This PC
    reg.exe add "$defaultUserHive\Software\Policies\Microsoft\Windows\Explorer" /v DisableSearchBoxSuggestions /t REG_DWORD /d 1 /f
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Search" /v SearchboxTaskbarMode /t REG_DWORD /d 3 /f # Icon only
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarDa /t REG_DWORD /d 0 /f # Disable Widgets
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarMn /t REG_DWORD /d 0 /f # Disable Chat

    # Show File Extensions
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v HideFileExt /t REG_DWORD /d 0 /f

    # Show "This PC" Icon on Desktop
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel" /v "{20D04FE0-3AEA-1069-A2D8-08002B30309D}" /t REG_DWORD /d 0 /f

    # Disable Sync Provider Notifications (Ads in File Explorer)
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v ShowSyncProviderNotifications /t REG_DWORD /d 0 /f

    # Enable Dark Mode (System and Apps)
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 0 /f
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 0 /f
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" /v EnableTransparency /t REG_DWORD /d 0 /f

    # Classic Context Menu (Windows 11)
    reg.exe add "$defaultUserHive\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /ve /t REG_SZ /d "" /f

    # Disable Lock Screen Tips, Tips and Suggestions, and Welcome Experience
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v RotatingLockScreenEnabled /t REG_DWORD /d 0 /f
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SubscribedContent-338387Enabled /t REG_DWORD /d 0 /f
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SoftLandingEnabled /t REG_DWORD /d 0 /f
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SubscribedContent-310093Enabled /t REG_DWORD /d 0 /f

    # Disable Copilot for Default User
    reg.exe add "$defaultUserHive\Software\Policies\Microsoft\Windows\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f

    # Enable End Task in Taskbar (Developer/Power User feature)
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarEndTask /t REG_DWORD /d 1 /f

    # Show Seconds in System Clock (Windows 11)
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v ShowSecondsInSystemClock /t REG_DWORD /d 1 /f

    # Disable "Finish setting up your device"
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\UserProfileEngagement" /v ScoobeSystemSettingEnabled /t REG_DWORD /d 0 /f

    # Disable Accessibility Shortcuts (Sticky Keys, Filter Keys, Toggle Keys)
    reg.exe add "$defaultUserHive\Control Panel\Accessibility\StickyKeys" /v Flags /t REG_SZ /d "506" /f
    reg.exe add "$defaultUserHive\Control Panel\Accessibility\Keyboard Response" /v Flags /t REG_SZ /d "122" /f
    reg.exe add "$defaultUserHive\Control Panel\Accessibility\ToggleKeys" /v Flags /t REG_SZ /d "58" /f

    # Disable Mouse Acceleration (Enhance Pointer Precision)
    reg.exe add "$defaultUserHive\Control Panel\Mouse" /v MouseSpeed /t REG_SZ /d "0" /f
    reg.exe add "$defaultUserHive\Control Panel\Mouse" /v MouseThreshold1 /t REG_SZ /d "0" /f
    reg.exe add "$defaultUserHive\Control Panel\Mouse" /v MouseThreshold2 /t REG_SZ /d "0" /f

    # Disable Typing Insights and Tailored Experiences
    reg.exe add "$defaultUserHive\Software\Microsoft\Input\TIPC" /v Enabled /t REG_DWORD /d 0 /f
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Privacy" /v TailoredExperiencesWithDiagnosticDataEnabled /t REG_DWORD /d 0 /f

    # Run UserOnce on first login (if script exists)
    # We wrap in cmd /c "if exist ..." to prevent errors for subsequent users after self-destruct
    $uScript = "C:\Windows\Setup\Scripts\UserOnce.ps1"
    $runOnceCmd = "cmd /c `"if exist \`"$uScript\`" powershell.exe -WindowStyle Normal -ExecutionPolicy Unrestricted -NoProfile -File \`"$uScript\`"`""
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\RunOnce" /v "UnattendedSetup" /t REG_SZ /d $runOnceCmd /f
}
catch {
    Write-Log "Error applying Default User tweaks: $_"
}
finally {
    # Only unload if we loaded it to avoid disrupting other processes
    if ($weLoadedIt) {
        Write-Log "Unloading Default User hive..."
        [GC]::Collect() # Force GC to release handles

        $maxRetries = 5
        $retry = 0
        $unloaded = $false

        while (-not $unloaded -and $retry -lt $maxRetries) {
            try {
                $result = reg.exe unload $defaultUserHive 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $unloaded = $true
                    Write-Log "Default User hive unloaded successfully."
                } else {
                    Write-Log "Failed to unload Default User hive (Attempt $($retry+1)): $result"
                    Start-Sleep -Seconds 2
                    [GC]::Collect()
                    $retry++
                }
            } catch {
                Write-Log "Exception unloading Default User hive (Attempt $($retry+1)): $_"
                Start-Sleep -Seconds 2
                $retry++
            }
        }

        if (-not $unloaded) {
            Write-Log "CRITICAL: Could not unload Default User hive after $maxRetries attempts."
        }
    }
}

Write-Log "Default User Configuration Completed."
