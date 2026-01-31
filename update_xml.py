import xml.etree.ElementTree as ET

# Define namespaces
namespaces = {
    'ua': 'urn:schemas-microsoft-com:unattend',
    'wcm': 'http://schemas.microsoft.com/WMIConfig/2002/State',
    'ext': 'https://schneegans.de/windows/unattend-generator/'
}

# Register namespaces for output
for prefix, uri in namespaces.items():
    if prefix == 'ua':
        ET.register_namespace('', uri)
    else:
        ET.register_namespace(prefix, uri)

# Content updates
helper_ps1 = r"""
function Get-InstallMedia {
    $drives = Get-PSDrive -PSProvider FileSystem
    foreach ($drive in $drives) {
        $path = Join-Path -Path $drive.Root -ChildPath "drivers"
        if (Test-Path -Path $path -PathType Container) {
            return $drive.Root
        }
    }
    return $null
}

function Get-InstallerFile {
    param([string]$Path)
    if (Test-Path -Path $Path) {
        $file = Get-ChildItem -Path $Path -Filter "*.exe" | Select-Object -First 1
        if ($file) { return $file.FullName }
    }
    return $null
}

function Write-Log {
    param(
        [string]$Message,
        [string]$Path = "$env:SystemRoot\Setup\Scripts\Setup.log"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Add-Content -Path $Path -Value $logEntry -ErrorAction SilentlyContinue
    # Write-Host is useful for debugging but we want total silence in production
    # Write-Host $logEntry
}

function Download-File {
    param(
        [string]$Url,
        [string]$Destination,
        [string]$Name = "File"
    )

    if ([string]::IsNullOrWhiteSpace($Url)) { return $false }

    Write-Log "Attempting to download $Name from $Url..."

    # Increase timeout to ~5 minutes (150 * 2s) to handle slow network initialization
    $maxRetries = 150
    $retry = 0
    $connected = $false

    # Wait for network
    while (-not $connected -and $retry -lt $maxRetries) {
        $testHosts = @("8.8.8.8", "1.1.1.1", "google.com")
        foreach ($host in $testHosts) {
            try {
                $null = [System.Net.Dns]::GetHostEntry($host)
                $connected = $true
                break
            } catch { }
        }

        if (-not $connected) {
            $retry++
            Start-Sleep -Seconds 2
        }
    }

    if ($connected) {
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri $Url -OutFile $Destination -UseBasicParsing -ErrorAction Stop
            if (Test-Path -Path $Destination -And (Get-Item $Destination).Length -gt 0) {
                Write-Log "Download of $Name successful."
                return $true
            }
        } catch {
            Write-Log "Failed to download $Name: $_"
        }
    } else {
        Write-Log "No network connectivity to download $Name."
    }
    return $false
}
"""

configure_privacy_ps1 = r"""
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-Log "Applying Privacy and Registry Tweaks..."

# Disable Telemetry and Data Collection
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v DoNotShowFeedbackNotifications /t REG_DWORD /d 1 /f
reg.exe add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f

# Disable Bing Search and Cortana
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v DisableWebSearch /t REG_DWORD /d 1 /f
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v ConnectedSearchUseWeb /t REG_DWORD /d 0 /f
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v AllowCloudSearch /t REG_DWORD /d 0 /f

# Disable Search Highlights
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v EnableDynamicContentInWSB /t REG_DWORD /d 0 /f

# Disable Online Tips and Suggestions
reg.exe add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v AllowOnlineTips /t REG_DWORD /d 0 /f

# Disable Copilot
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f
reg.exe add "HKCU\Software\Policies\Microsoft\Windows\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f

# Disable News and Interests
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Dsh" /v AllowNewsAndInterests /t REG_DWORD /d 0 /f

# Disable Edge First Run and Bloat
reg.exe add "HKLM\Software\Policies\Microsoft\Edge" /v HideFirstRunExperience /t REG_DWORD /d 1 /f
reg.exe add "HKLM\Software\Policies\Microsoft\Edge\Recommended" /v BackgroundModeEnabled /t REG_DWORD /d 0 /f
reg.exe add "HKLM\Software\Policies\Microsoft\Edge\Recommended" /v StartupBoostEnabled /t REG_DWORD /d 0 /f

# Disable BitLocker Automatic Device Encryption
reg.exe add "HKLM\SYSTEM\CurrentControlSet\Control\BitLocker" /v "PreventDeviceEncryption" /t REG_DWORD /d 1 /f

# Disable VBS/HVCI (Performance)
reg.exe add "HKLM\System\CurrentControlSet\Control\DeviceGuard" /v "EnableVirtualizationBasedSecurity" /t REG_DWORD /d 0 /f
reg.exe add "HKLM\System\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity" /v "Enabled" /t REG_DWORD /d 0 /f

# Disable Telemetry and Maps Services
$services = @('DiagTrack', 'dmwappushservice', 'MapsBroker', 'lfsvc')
foreach ($service in $services) {
    if (Get-Service -Name $service -ErrorAction SilentlyContinue) {
        Write-Log "Disabling service $service..."
        try {
            Stop-Service -Name $service -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path "Registry::HKLM\SYSTEM\CurrentControlSet\Services\$service" -Name "Start" -Value 4 -Type DWord -Force -ErrorAction SilentlyContinue
        } catch {
            Write-Log "Failed to disable service $service: $_"
        }
    }
}

Write-Log "Privacy Tweaks Applied."
"""

default_user_ps1 = r"""
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-Log "Configuring Default User..."

# Load Default User Hive
$defaultUserHive = "HKU\DefaultUser"
reg.exe load $defaultUserHive "C:\Users\Default\NTUSER.DAT"

try {
    # Taskbar and Explorer settings
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v ShowTaskViewButton /t REG_DWORD /d 0 /f
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v TaskbarAl /t REG_DWORD /d 0 /f # Left align taskbar
    reg.exe add "$defaultUserHive\Software\Policies\Microsoft\Windows\Explorer" /v DisableSearchBoxSuggestions /t REG_DWORD /d 1 /f

    # Show File Extensions
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v HideFileExt /t REG_DWORD /d 0 /f

    # Dark Mode (Apps and System)
    $themeKey = "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    reg.exe add $themeKey /v AppsUseLightTheme /t REG_DWORD /d 0 /f
    reg.exe add $themeKey /v SystemUsesLightTheme /t REG_DWORD /d 0 /f

    # Disable Lock Screen Tips and Tricks
    $contentDelivery = "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
    reg.exe add $contentDelivery /v RotatingLockScreenEnabled /t REG_DWORD /d 0 /f
    reg.exe add $contentDelivery /v RotatingLockScreenOverlayEnabled /t REG_DWORD /d 0 /f
    reg.exe add $contentDelivery /v SubscribedContent-338387Enabled /t REG_DWORD /d 0 /f

    # Classic Context Menu (Windows 11)
    reg.exe add "$defaultUserHive\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /ve /t REG_SZ /d "" /f

    # Disable Copilot for Default User
    reg.exe add "$defaultUserHive\Software\Policies\Microsoft\Windows\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f

    # Run UserOnce on first login
    reg.exe add "$defaultUserHive\Software\Microsoft\Windows\CurrentVersion\RunOnce" /v "UnattendedSetup" /t REG_SZ /d "powershell.exe -WindowStyle `"Normal`" -ExecutionPolicy `"Unrestricted`" -NoProfile -File `"C:\Windows\Setup\Scripts\UserOnce.ps1`"" /f
}
finally {
    reg.exe unload $defaultUserHive
    [GC]::Collect()
}

Write-Log "Default User Configuration Completed."
"""

specialize_ps1 = r"""
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

$scripts = @(
    "$PSScriptRoot\Drivers\Install-Network.ps1",
    "$PSScriptRoot\Tweaks\Remove-Bloatware.ps1",
    "$PSScriptRoot\Tweaks\Configure-Privacy.ps1",
    "$PSScriptRoot\Tweaks\Optimize-System.ps1",
    "$PSScriptRoot\Drivers\Install-Nvidia.ps1",
    "$PSScriptRoot\Drivers\Install-AMD.ps1",
    "$PSScriptRoot\Drivers\Install-Focusrite.ps1",
    "$PSScriptRoot\Apps\Install-Runtimes.ps1",
    "$PSScriptRoot\Apps\Install-Chrome.ps1",
    "$PSScriptRoot\Tweaks\SetStartPins.ps1"
)

Write-Log "Starting Specialize Pass (Optimized)..."

foreach ($script in $scripts) {
    if (Test-Path $script) {
        Write-Log "Executing $script..."
        try {
            & $script
        } catch {
            Write-Log "Error executing $script: $_"
        }
    } else {
        Write-Log "Script not found: $script"
    }
}

# Generate SetupComplete.cmd for post-OOBE cleanup
# This ensures unattend.xml remains available for OOBE but is removed before login
$setupCompleteContent = @"
del /q /f "%WINDIR%\Panther\unattend.xml"
del /q /f "%WINDIR%\Panther\unattend-original.xml"
rd /s /q "%WINDIR%\Setup\Scripts"
"@

$setupCompletePath = "$env:SystemRoot\Setup\Scripts\SetupComplete.cmd"
try {
    Set-Content -Path $setupCompletePath -Value $setupCompleteContent -Force
    Write-Log "Generated SetupComplete.cmd for cleanup."
} catch {
    Write-Log "Error creating SetupComplete.cmd: $_"
}

Write-Log "Specialize Pass Completed."
"""

updates = {
    r"C:\Windows\Setup\Scripts\Lib\Helper.ps1": helper_ps1.strip(),
    r"C:\Windows\Setup\Scripts\Tweaks\Configure-Privacy.ps1": configure_privacy_ps1.strip(),
    r"C:\Windows\Setup\Scripts\DefaultUser.ps1": default_user_ps1.strip(),
    r"C:\Windows\Setup\Scripts\Specialize.ps1": specialize_ps1.strip(),
}

tree = ET.parse('autounattend.xml')
root = tree.getroot()

# Find the Extensions element
# It usually is a direct child of 'unattend', but let's find it.
# The namespace for Extensions is 'https://schneegans.de/windows/unattend-generator/'
ext_ns = '{https://schneegans.de/windows/unattend-generator/}'
extensions = root.find(f".//{ext_ns}Extensions")

if extensions is not None:
    for file_node in extensions.findall(f"{ext_ns}File"):
        path = file_node.get('path')
        if path in updates:
            print(f"Updating {path}...")
            file_node.text = '\n' + updates[path] + '\n'
else:
    print("Could not find Extensions node!")

tree.write('autounattend.xml', encoding='utf-8', xml_declaration=True)
print("autounattend.xml updated successfully.")
