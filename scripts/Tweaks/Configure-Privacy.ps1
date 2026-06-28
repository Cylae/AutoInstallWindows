
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-SetupLog "Applying Privacy and Registry Tweaks..."

# Disable Telemetry and Data Collection
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v DoNotShowFeedbackNotifications /t REG_DWORD /d 1 /f
reg.exe add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f

# Disable Windows Error Reporting
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Error Reporting" /v Disabled /t REG_DWORD /d 1 /f

# Disable Shared Experiences / Activity History
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v EnableActivityFeed /t REG_DWORD /d 0 /f
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v PublishUserActivities /t REG_DWORD /d 0 /f
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v UploadUserActivities /t REG_DWORD /d 0 /f

# Disable Consumer Features (Auto-installed apps)
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent" /v DisableWindowsConsumerFeatures /t REG_DWORD /d 1 /f

# Disable Bing Search, Cortana, and Search Highlights
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v DisableWebSearch /t REG_DWORD /d 1 /f
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v ConnectedSearchUseWeb /t REG_DWORD /d 0 /f
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v AllowCloudSearch /t REG_DWORD /d 0 /f
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v EnableDynamicContentInWS /t REG_DWORD /d 0 /f

# Disable Copilot and Recall (AI Screenshot)
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v DisableAIDataAnalysis /t REG_DWORD /d 1 /f

# Disable News and Interests (Widgets), Search Highlights, and Meet Now
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Dsh" /v AllowNewsAndInterests /t REG_DWORD /d 0 /f
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v EnableSearchHighlights /t REG_DWORD /d 0 /f
reg.exe add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v HideSCAMeetNow /t REG_DWORD /d 1 /f

# Disable Online Tips and Advertising ID
reg.exe add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v AllowOnlineTips /t REG_DWORD /d 0 /f
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo" /v DisabledByGroupPolicy /t REG_DWORD /d 1 /f

# Disable Edge First Run and Bloat
reg.exe add "HKLM\Software\Policies\Microsoft\Edge" /v HideFirstRunExperience /t REG_DWORD /d 1 /f
reg.exe add "HKLM\Software\Policies\Microsoft\Edge" /v BackgroundModeEnabled /t REG_DWORD /d 0 /f
reg.exe add "HKLM\Software\Policies\Microsoft\Edge" /v StartupBoostEnabled /t REG_DWORD /d 0 /f

# Disable Location Tracking
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors" /v DisableLocation /t REG_DWORD /d 1 /f

# Disable Delivery Optimization
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization" /v DODownloadMode /t REG_DWORD /d 0 /f

# Disable BitLocker Automatic Device Encryption
reg.exe add "HKLM\SYSTEM\CurrentControlSet\Control\BitLocker" /v "PreventDeviceEncryption" /t REG_DWORD /d 1 /f

# Disable VBS/HVCI (Performance)
reg.exe add "HKLM\System\CurrentControlSet\Control\DeviceGuard" /v "EnableVirtualizationBasedSecurity" /t REG_DWORD /d 0 /f
reg.exe add "HKLM\System\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity" /v "Enabled" /t REG_DWORD /d 0 /f

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
