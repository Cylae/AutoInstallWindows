
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
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "ShowTaskViewButton" -Type "DWord" -Value 0
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarAl" -Type "DWord" -Value 0 # Left align taskbar
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "LaunchTo" -Type "DWord" -Value 1 # Open This PC
    Set-RegistryKey -Path "$defaultUserHive\Software\Policies\Microsoft\Windows\Explorer" -Name "DisableSearchBoxSuggestions" -Type "DWord" -Value 1
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Search" -Name "SearchboxTaskbarMode" -Type "DWord" -Value 3 # Icon only
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarDa" -Type "DWord" -Value 0 # Disable Widgets
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarMn" -Type "DWord" -Value 0 # Disable Chat

    # Show File Extensions
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "HideFileExt" -Type "DWord" -Value 0

    # Show "This PC" Icon on Desktop
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel" -Name "{20D04FE0-3AEA-1069-A2D8-08002B30309D}" -Type "DWord" -Value 0

    # Disable Sync Provider Notifications (Ads in File Explorer)
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "ShowSyncProviderNotifications" -Type "DWord" -Value 0

    # Enable Dark Mode (System and Apps)
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name "AppsUseLightTheme" -Type "DWord" -Value 0
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name "SystemUsesLightTheme" -Type "DWord" -Value 0
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name "EnableTransparency" -Type "DWord" -Value 0

    # Classic Context Menu (Windows 11)
    Set-RegistryKey -Path "$defaultUserHive\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" -Name "" -Type "String" -Value ""

    # Disable Lock Screen Tips, Tips and Suggestions, and Welcome Experience
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "RotatingLockScreenEnabled" -Type "DWord" -Value 0
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SubscribedContent-338387Enabled" -Type "DWord" -Value 0
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SoftLandingEnabled" -Type "DWord" -Value 0
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SubscribedContent-310093Enabled" -Type "DWord" -Value 0

    # Disable Copilot for Default User
    Set-RegistryKey -Path "$defaultUserHive\Software\Policies\Microsoft\Windows\WindowsCopilot" -Name "TurnOffWindowsCopilot" -Type "DWord" -Value 1

    # Enable End Task in Taskbar (Developer/Power User feature)
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarEndTask" -Type "DWord" -Value 1

    # Show Seconds in System Clock (Windows 11)
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "ShowSecondsInSystemClock" -Type "DWord" -Value 1

    # Disable "Finish setting up your device"
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\UserProfileEngagement" -Name "ScoobeSystemSettingEnabled" -Type "DWord" -Value 0

    # Disable Accessibility Shortcuts (Sticky Keys, Filter Keys, Toggle Keys)
    Set-RegistryKey -Path "$defaultUserHive\Control Panel\Accessibility\StickyKeys" -Name "Flags" -Type "String" -Value "506"
    Set-RegistryKey -Path "$defaultUserHive\Control Panel\Accessibility\Keyboard Response" -Name "Flags" -Type "String" -Value "122"
    Set-RegistryKey -Path "$defaultUserHive\Control Panel\Accessibility\ToggleKeys" -Name "Flags" -Type "String" -Value "58"

    # Disable Mouse Acceleration (Enhance Pointer Precision)
    Set-RegistryKey -Path "$defaultUserHive\Control Panel\Mouse" -Name "MouseSpeed" -Type "String" -Value "0"
    Set-RegistryKey -Path "$defaultUserHive\Control Panel\Mouse" -Name "MouseThreshold1" -Type "String" -Value "0"
    Set-RegistryKey -Path "$defaultUserHive\Control Panel\Mouse" -Name "MouseThreshold2" -Type "String" -Value "0"

    # Disable Typing Insights and Tailored Experiences
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Input\TIPC" -Name "Enabled" -Type "DWord" -Value 0
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Privacy" -Name "TailoredExperiencesWithDiagnosticDataEnabled" -Type "DWord" -Value 0

    # Run UserOnce on first login (if script exists)
    # We wrap in cmd /c "if exist ..." to prevent errors for subsequent users after self-destruct
    $uScript = "C:\Windows\Setup\Scripts\UserOnce.ps1"
    $runOnceCmd = "cmd /c `"if exist \`"$uScript\`" powershell.exe -WindowStyle Hidden -ExecutionPolicy Unrestricted -NoProfile -File \`"$uScript\`"`""
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\RunOnce" -Name "UnattendedSetup" -Type "String" -Value $runOnceCmd
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
