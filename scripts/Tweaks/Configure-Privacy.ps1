
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-Log "Applying Privacy and Registry Tweaks..."

# Disable Telemetry and Data Collection
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Value 0 -Type "REG_DWORD"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "DoNotShowFeedbackNotifications" -Value 1 -Type "REG_DWORD"
Set-RegistryKey -Path "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" -Name "AllowTelemetry" -Value 0 -Type "REG_DWORD"

# Disable Windows Error Reporting
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Error Reporting" -Name "Disabled" -Value 1 -Type "REG_DWORD"

# Disable Shared Experiences / Activity History
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" -Name "EnableActivityFeed" -Value 0 -Type "REG_DWORD"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" -Name "PublishUserActivities" -Value 0 -Type "REG_DWORD"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" -Name "UploadUserActivities" -Value 0 -Type "REG_DWORD"

# Disable Consumer Features (Auto-installed apps)
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent" -Name "DisableWindowsConsumerFeatures" -Value 1 -Type "REG_DWORD"

# Disable Bing Search, Cortana, and Search Highlights
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "AllowCortana" -Value 0 -Type "REG_DWORD"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "DisableWebSearch" -Value 1 -Type "REG_DWORD"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "ConnectedSearchUseWeb" -Value 0 -Type "REG_DWORD"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "AllowCloudSearch" -Value 0 -Type "REG_DWORD"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "EnableDynamicContentInWS" -Value 0 -Type "REG_DWORD"

# Disable Copilot and Recall (AI Screenshot)
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" -Name "TurnOffWindowsCopilot" -Value 1 -Type "REG_DWORD"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" -Name "DisableAIDataAnalysis" -Value 1 -Type "REG_DWORD"

# Disable News and Interests (Widgets), Search Highlights, and Meet Now
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Dsh" -Name "AllowNewsAndInterests" -Value 0 -Type "REG_DWORD"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "EnableSearchHighlights" -Value 0 -Type "REG_DWORD"
Set-RegistryKey -Path "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" -Name "HideSCAMeetNow" -Value 1 -Type "REG_DWORD"

# Disable Online Tips and Advertising ID
Set-RegistryKey -Path "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" -Name "AllowOnlineTips" -Value 0 -Type "REG_DWORD"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo" -Name "DisabledByGroupPolicy" -Value 1 -Type "REG_DWORD"

# Disable Edge First Run and Bloat
Set-RegistryKey -Path "HKLM\Software\Policies\Microsoft\Edge" -Name "HideFirstRunExperience" -Value 1 -Type "REG_DWORD"
Set-RegistryKey -Path "HKLM\Software\Policies\Microsoft\Edge" -Name "BackgroundModeEnabled" -Value 0 -Type "REG_DWORD"
Set-RegistryKey -Path "HKLM\Software\Policies\Microsoft\Edge" -Name "StartupBoostEnabled" -Value 0 -Type "REG_DWORD"

# Disable Location Tracking
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors" -Name "DisableLocation" -Value 1 -Type "REG_DWORD"

# Disable Delivery Optimization
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization" -Name "DODownloadMode" -Value 0 -Type "REG_DWORD"

# Disable BitLocker Automatic Device Encryption
Set-RegistryKey -Path "HKLM\SYSTEM\CurrentControlSet\Control\BitLocker" -Name "PreventDeviceEncryption" -Value 1 -Type "REG_DWORD"

# Disable VBS/HVCI (Performance)
Set-RegistryKey -Path "HKLM\System\CurrentControlSet\Control\DeviceGuard" -Name "EnableVirtualizationBasedSecurity" -Value 0 -Type "REG_DWORD"
Set-RegistryKey -Path "HKLM\System\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity" -Name "Enabled" -Value 0 -Type "REG_DWORD"

# Disable Telemetry and Maps Services
$services = @('DiagTrack', 'dmwappushservice', 'MapsBroker', 'lfsvc')
foreach ($service in $services) {
    if (Get-Service -Name $service -ErrorAction SilentlyContinue) {
        Write-Log "Disabling service $service..."
        try {
            Stop-Service -Name $service -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path "Registry::HKLM\SYSTEM\CurrentControlSet\Services\$service" -Name "Start" -Value 4 -Type DWord -Force -ErrorAction SilentlyContinue
        } catch {
            Write-Log "Failed to disable service $($service): $_"
        }
    }
}

Write-Log "Privacy Tweaks Applied."
