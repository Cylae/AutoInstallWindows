
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-SetupLog "Applying Privacy and Registry Tweaks..."

# Disable Telemetry and Data Collection
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Type "DWord" -Value "0"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "DoNotShowFeedbackNotifications" -Type "DWord" -Value "1"
Set-RegistryKey -Path "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" -Name "AllowTelemetry" -Type "DWord" -Value "0"

# Disable Windows Error Reporting
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Error Reporting" -Name "Disabled" -Type "DWord" -Value "1"

# Disable Shared Experiences / Activity History
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" -Name "EnableActivityFeed" -Type "DWord" -Value "0"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" -Name "PublishUserActivities" -Type "DWord" -Value "0"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" -Name "UploadUserActivities" -Type "DWord" -Value "0"

# Disable Consumer Features (Auto-installed apps)
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent" -Name "DisableWindowsConsumerFeatures" -Type "DWord" -Value "1"

# Disable Bing Search, Cortana, and Search Highlights
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "AllowCortana" -Type "DWord" -Value "0"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "DisableWebSearch" -Type "DWord" -Value "1"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "ConnectedSearchUseWeb" -Type "DWord" -Value "0"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "AllowCloudSearch" -Type "DWord" -Value "0"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "EnableDynamicContentInWS" -Type "DWord" -Value "0"

# Disable Copilot and Recall (AI Screenshot)
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" -Name "TurnOffWindowsCopilot" -Type "DWord" -Value "1"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" -Name "DisableAIDataAnalysis" -Type "DWord" -Value "1"

# Disable News and Interests (Widgets), Search Highlights, and Meet Now
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Dsh" -Name "AllowNewsAndInterests" -Type "DWord" -Value "0"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "EnableSearchHighlights" -Type "DWord" -Value "0"
Set-RegistryKey -Path "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" -Name "HideSCAMeetNow" -Type "DWord" -Value "1"

# Disable Online Tips and Advertising ID
Set-RegistryKey -Path "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" -Name "AllowOnlineTips" -Type "DWord" -Value "0"
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo" -Name "DisabledByGroupPolicy" -Type "DWord" -Value "1"

# Disable Edge First Run and Bloat
Set-RegistryKey -Path "HKLM\Software\Policies\Microsoft\Edge" -Name "HideFirstRunExperience" -Type "DWord" -Value "1"
Set-RegistryKey -Path "HKLM\Software\Policies\Microsoft\Edge" -Name "BackgroundModeEnabled" -Type "DWord" -Value "0"
Set-RegistryKey -Path "HKLM\Software\Policies\Microsoft\Edge" -Name "StartupBoostEnabled" -Type "DWord" -Value "0"

# Disable Location Tracking
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors" -Name "DisableLocation" -Type "DWord" -Value "1"

# Disable Delivery Optimization
Set-RegistryKey -Path "HKLM\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization" -Name "DODownloadMode" -Type "DWord" -Value "0"

# Disable BitLocker Automatic Device Encryption
Set-RegistryKey -Path "HKLM\SYSTEM\CurrentControlSet\Control\BitLocker" -Name "PreventDeviceEncryption" -Type "DWord" -Value "1"

# Disable VBS/HVCI (Performance)
Set-RegistryKey -Path "HKLM\System\CurrentControlSet\Control\DeviceGuard" -Name "EnableVirtualizationBasedSecurity" -Type "DWord" -Value "0"
Set-RegistryKey -Path "HKLM\System\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity" -Name "Enabled" -Type "DWord" -Value "0"

# Disable Telemetry and Maps Services
$services = @('DiagTrack', 'dmwappushservice', 'MapsBroker', 'lfsvc')
foreach ($service in $services) {
    if (Get-Service -Name $service -ErrorAction SilentlyContinue) {
        Write-SetupLog "Disabling service $service..."
        try {
            Stop-Service -Name $service -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path "Registry::HKLM\SYSTEM\CurrentControlSet\Services\$service" -Name "Start" -Value 4 -Type DWord -Force -ErrorAction SilentlyContinue
        } catch {
            Write-SetupLog "Failed to disable service $($service): $_"
        }
    }
}

Write-SetupLog "Privacy Tweaks Applied."
