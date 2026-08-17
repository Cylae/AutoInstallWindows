
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-SetupLog "Configuring Default User..."

# Load Default User Hive
$defaultUserHive = "HKU\DefaultUser"
$weLoadedIt = $false

# Robustly load hive: Check if already loaded first
if (-not (Test-Path "Registry::$defaultUserHive")) {
    Write-SetupLog "Loading Default User hive..."
    try {
        $result = reg.exe load $defaultUserHive "C:\Users\Default\NTUSER.DAT" 2>&1
        if ($LASTEXITCODE -eq 0) {
            $weLoadedIt = $true
        } else {
            Write-SetupLog "Failed to load Default User hive: $result"
            return
        }
    } catch {
        Write-SetupLog "Exception loading Default User hive: $_"
        return
    }
} else {
    Write-SetupLog "Default User hive already loaded."
}

try {
    # Taskbar and Explorer settings
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "ShowTaskViewButton" -Value "0" -Type "DWord"
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarAl" -Value "0" -Type "DWord" # Left align taskbar
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "LaunchTo" -Value "1" -Type "DWord" # Open This PC
    Set-RegistryKey -Path "$defaultUserHive\Software\Policies\Microsoft\Windows\Explorer" -Name "DisableSearchBoxSuggestions" -Value "1" -Type "DWord"
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Search" -Name "SearchboxTaskbarMode" -Value "3" -Type "DWord" # Icon only
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarDa" -Value "0" -Type "DWord" # Disable Widgets
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarMn" -Value "0" -Type "DWord" # Disable Chat

    # Show File Extensions
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "HideFileExt" -Value "0" -Type "DWord"

    # Show "This PC" Icon on Desktop
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel" -Name "{20D04FE0-3AEA-1069-A2D8-08002B30309D}" -Value "0" -Type "DWord"

    # Disable Sync Provider Notifications (Ads in File Explorer)
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "ShowSyncProviderNotifications" -Value "0" -Type "DWord"

    # Enable Dark Mode (System and Apps)
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name "AppsUseLightTheme" -Value "0" -Type "DWord"
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name "SystemUsesLightTheme" -Value "0" -Type "DWord"
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name "EnableTransparency" -Value "0" -Type "DWord"

    # Classic Context Menu (Windows 11)
    Set-RegistryKey -Path "$defaultUserHive\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" -Name "" -Value "" -Type "String"

    # Disable Lock Screen Tips, Tips and Suggestions, and Welcome Experience
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "RotatingLockScreenEnabled" -Value "0" -Type "DWord"
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SubscribedContent-338387Enabled" -Value "0" -Type "DWord"
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SoftLandingEnabled" -Value "0" -Type "DWord"
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SubscribedContent-310093Enabled" -Value "0" -Type "DWord"

    # Disable Copilot for Default User
    Set-RegistryKey -Path "$defaultUserHive\Software\Policies\Microsoft\Windows\WindowsCopilot" -Name "TurnOffWindowsCopilot" -Value "1" -Type "DWord"

    # Enable End Task in Taskbar (Developer/Power User feature)
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarEndTask" -Value "1" -Type "DWord"

    # Show Seconds in System Clock (Windows 11)
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "ShowSecondsInSystemClock" -Value "1" -Type "DWord"

    # Disable "Finish setting up your device"
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\UserProfileEngagement" -Name "ScoobeSystemSettingEnabled" -Value "0" -Type "DWord"

    # Disable Accessibility Shortcuts (Sticky Keys, Filter Keys, Toggle Keys)
    Set-RegistryKey -Path "$defaultUserHive\Control Panel\Accessibility\StickyKeys" -Name "Flags" -Value "506" -Type "String"
    Set-RegistryKey -Path "$defaultUserHive\Control Panel\Accessibility\Keyboard Response" -Name "Flags" -Value "122" -Type "String"
    Set-RegistryKey -Path "$defaultUserHive\Control Panel\Accessibility\ToggleKeys" -Name "Flags" -Value "58" -Type "String"

    # Disable Mouse Acceleration (Enhance Pointer Precision)
    Set-RegistryKey -Path "$defaultUserHive\Control Panel\Mouse" -Name "MouseSpeed" -Value "0" -Type "String"
    Set-RegistryKey -Path "$defaultUserHive\Control Panel\Mouse" -Name "MouseThreshold1" -Value "0" -Type "String"
    Set-RegistryKey -Path "$defaultUserHive\Control Panel\Mouse" -Name "MouseThreshold2" -Value "0" -Type "String"

    # Disable Typing Insights and Tailored Experiences
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Input\TIPC" -Name "Enabled" -Value "0" -Type "DWord"
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Privacy" -Name "TailoredExperiencesWithDiagnosticDataEnabled" -Value "0" -Type "DWord"

    # Run UserOnce on first login (if script exists)
    # We wrap in cmd /c "if exist ..." to prevent errors for subsequent users after self-destruct
    $uScript = "C:\Windows\Setup\Scripts\UserOnce.ps1"
    $runOnceCmd = "cmd /c `"if exist \`"$uScript\`" powershell.exe -WindowStyle Hidden -ExecutionPolicy Unrestricted -NoProfile -File \`"$uScript\`"`""
    Set-RegistryKey -Path "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\RunOnce" -Name "UnattendedSetup" -Value $runOnceCmd -Type "String"
}
catch {
    Write-SetupLog "Error applying Default User tweaks: $_"
}
finally {
    # Only unload if we loaded it to avoid disrupting other processes
    if ($weLoadedIt) {
        Write-SetupLog "Unloading Default User hive..."
        [GC]::Collect() # Force GC to release handles

        $maxRetries = 5
        $retry = 0
        $unloaded = $false

        while (-not $unloaded -and $retry -lt $maxRetries) {
            try {
                $result = reg.exe unload $defaultUserHive 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $unloaded = $true
                    Write-SetupLog "Default User hive unloaded successfully."
                } else {
                    Write-SetupLog "Failed to unload Default User hive (Attempt $($retry+1)): $result"
                    Start-Sleep -Seconds 2
                    [GC]::Collect()
                    $retry++
                }
            } catch {
                Write-SetupLog "Exception unloading Default User hive (Attempt $($retry+1)): $_"
                Start-Sleep -Seconds 2
                $retry++
            }
        }

        if (-not $unloaded) {
            Write-SetupLog "CRITICAL: Could not unload Default User hive after $maxRetries attempts."
        }
    }
}

Write-SetupLog "Default User Configuration Completed."
