import re

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
    $testHosts = @("8.8.8.8", "1.1.1.1", "google.com", "microsoft.com")

    # Wait for network
    while (-not $connected -and $retry -lt $maxRetries) {
        foreach ($h in $testHosts) {
            try {
                $null = [System.Net.Dns]::GetHostEntry($h)
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

nvidia_ps1 = r"""
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

# OPTIONAL: Set a direct download URL for the Nvidia Driver here.
$DownloadUrl = ""

Write-Log "Starting Nvidia Driver Installation..."
$mediaRoot = Get-InstallMedia
$setupPath = $null

# Online check removed due to API deprecation.
# To use a direct download, set the URL above manually.

# Try Local (Primary)
if ($mediaRoot) {
    Write-Log "Checking local storage..."
    $driverDir = Join-Path -Path $mediaRoot -ChildPath "drivers\nvidia"
    $setupPath = Get-InstallerFile -Path $driverDir
}

# Try Download (Fallback if URL provided)
if (-not $setupPath -and $DownloadUrl) {
    $dest = "$env:TEMP\nvidia_driver.exe"
    if (Download-File -Url $DownloadUrl -Destination $dest -Name "Nvidia Driver") {
        $setupPath = $dest
    }
}

if ($setupPath) {
    Write-Log "Installing Nvidia driver from $setupPath..."
    try {
        Unblock-File -Path $setupPath -ErrorAction SilentlyContinue
        # -s: Silent, -n: No splash, -f: Force, -noreboot: No reboot
        Start-Process -FilePath $setupPath -ArgumentList '-s -n -f -noreboot' -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\nvidia_install.log"
        Write-Log "Nvidia driver installation completed."
    }
    catch {
        Write-Log "Error installing Nvidia drivers: $_"
    }
} else {
    Write-Log "Nvidia installer not found locally and no download URL provided."
}
"""

privacy_ps1 = r"""
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

# Disable Search Highlights (Windows 11)
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v EnableDynamicContentInWSB /t REG_DWORD /d 0 /f

# Disable Copilot
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f
reg.exe add "HKCU\Software\Policies\Microsoft\Windows\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f

# Disable News and Interests
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Dsh" /v AllowNewsAndInterests /t REG_DWORD /d 0 /f

# Disable Online Tips
reg.exe add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v AllowOnlineTips /t REG_DWORD /d 0 /f

# Disable Advertising ID
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo" /v DisabledByGroupPolicy /t REG_DWORD /d 1 /f

# Disable Tailored Experiences
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent" /v DisableTailoredExperiencesWithDiagnosticData /t REG_DWORD /d 1 /f
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent" /v DisableWindowsConsumerFeatures /t REG_DWORD /d 1 /f

# Disable Edge First Run and Bloat
reg.exe add "HKLM\Software\Policies\Microsoft\Edge" /v HideFirstRunExperience /t REG_DWORD /d 1 /f
reg.exe add "HKLM\Software\Policies\Microsoft\Edge\Recommended" /v BackgroundModeEnabled /t REG_DWORD /d 0 /f
reg.exe add "HKLM\Software\Policies\Microsoft\Edge\Recommended" /v StartupBoostEnabled /t REG_DWORD /d 0 /f

# Disable BitLocker Automatic Device Encryption
reg.exe add "HKLM\SYSTEM\CurrentControlSet\Control\BitLocker" /v "PreventDeviceEncryption" /t REG_DWORD /d 1 /f

# Disable VBS/HVCI (Performance)
reg.exe add "HKLM\System\CurrentControlSet\Control\DeviceGuard" /v "EnableVirtualizationBasedSecurity" /t REG_DWORD /d 0 /f
reg.exe add "HKLM\System\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity" /v "Enabled" /t REG_DWORD /d 0 /f

# Classic Context Menu (Windows 11) - Requires HKCU, handled in UserOnce or DefaultUser
# Here we can try setting it for default user via reg load or just rely on UserOnce

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

useronce_ps1 = r'''
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-Log "Configuring User Account..."

# Disable Copilot
Get-AppxPackage -Name 'Microsoft.Windows.Ai.Copilot.Provider' | Remove-AppxPackage -ErrorAction SilentlyContinue

# Explorer Settings
Set-ItemProperty -LiteralPath 'Registry::HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced' -Name 'LaunchTo' -Type 'DWord' -Value 1 -Force
Set-ItemProperty -LiteralPath 'Registry::HKCU\Software\Microsoft\Windows\CurrentVersion\Search' -Name 'SearchboxTaskbarMode' -Type 'DWord' -Value 3 -Force # Icon only

# Restart Explorer to apply changes
Get-Process -Name 'explorer' -ErrorAction 'SilentlyContinue' | Stop-Process -Force

# Register Daily Winget Auto-Update Task (Transparent)
$taskName = "DailySoftwareUpdate"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -Command `"winget source update; winget upgrade --all --include-unknown --silent --accept-source-agreements --accept-package-agreements`""
$trigger = New-ScheduledTaskTrigger -Daily -At 13:00
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -Hidden -RunOnlyIfNetworkAvailable
Register-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -TaskName $taskName -Description "Automatically updates all software via Winget silently." -RunLevel Highest -Force | Out-Null
Write-Log "Registered Daily Winget Auto-Update Task."

Write-Log "User Configuration Completed."

# Self-destruct: remove the Scripts directory
# We use a detached cmd process to avoid file locking issues since this script is running from that directory.
Start-Process -FilePath "cmd.exe" -ArgumentList "/c timeout /t 5 /nobreak > NUL & rmdir /s /q ""C:\Windows\Setup\Scripts""" -WindowStyle Hidden
'''

def escape_xml(content):
    content = content.replace("&", "&amp;")
    content = content.replace("\"", "&quot;")
    content = content.replace("<", "&lt;")
    content = content.replace(">", "&gt;")
    return content

files_to_update = {
    r'C:\Windows\Setup\Scripts\Lib\Helper.ps1': helper_ps1,
    r'C:\Windows\Setup\Scripts\Drivers\Install-Nvidia.ps1': nvidia_ps1,
    r'C:\Windows\Setup\Scripts\Tweaks\Configure-Privacy.ps1': privacy_ps1,
    r'C:\Windows\Setup\Scripts\UserOnce.ps1': useronce_ps1
}

with open("autounattend.xml", "r", encoding="utf-8") as f:
    xml_content = f.read()

for path, new_code in files_to_update.items():
    escaped_code = escape_xml(new_code.strip())
    # Regex to find the File block.
    # We look for <File path="PATH"> ... </File>
    # The path needs to be escaped for regex
    escaped_path = re.escape(path)
    pattern = r'(<File path="' + escaped_path + r'">)(.*?)(</File>)'

    match = re.search(pattern, xml_content, re.DOTALL)
    if match:
        print(f"Updating {path}...")

        def replacer(m):
            return f'{m.group(1)}\n{escaped_code}\n{m.group(3)}'

        xml_content = re.sub(pattern, replacer, xml_content, flags=re.DOTALL, count=1)

    else:
        print(f"Warning: Could not find File block for {path}")

with open("autounattend.xml", "w", encoding="utf-8") as f:
    f.write(xml_content)

print("Done.")
