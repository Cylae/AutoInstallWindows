import re

# Read the file
with open('autounattend.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# Helper function to replace content of a File tag
def replace_file_content(xml_content, file_path, new_content):
    # Escape special characters for regex
    # The pattern looks for <File path="...">Content</File>
    # We use non-greedy match for content
    pattern = r'(<File path="' + re.escape(file_path) + r'">)(.*?)(</File>)'

    # Check if file exists
    if not re.search(pattern, xml_content, re.DOTALL):
        print(f"Warning: File path {file_path} not found in XML.")
        return xml_content

    def replacement(match):
        return match.group(1) + '\n' + new_content.strip() + '\n' + match.group(3)

    return re.sub(pattern, replacement, xml_content, flags=re.DOTALL)

def xml_encode(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    return s

# New content for Helper.ps1
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
        [string]$Path = "$env:SystemRoot\Panther\Autounattend_Log.txt"
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
        try {
            $null = [System.Net.Dns]::GetHostEntry("8.8.8.8")
            $connected = $true
        } catch {
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

# New content for Install-Network.ps1
install_network_ps1 = r"""
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-Log "Starting Network Driver Installation..."
$mediaRoot = Get-InstallMedia

if ($mediaRoot) {
    $driverPath = Join-Path -Path $mediaRoot -ChildPath "drivers\network"
    if (Test-Path -Path $driverPath) {
        Write-Log "Found network drivers path at $driverPath"
        # Check if there are any INF files to avoid pnputil error
        if (Get-ChildItem -Path $driverPath -Filter "*.inf" -Recurse) {
            try {
                $pnputilArgs = "/add-driver `"$driverPath\*.inf`" /subdirs /install"
                # Redirect standard output/error to null for total silence
                Start-Process -FilePath "pnputil.exe" -ArgumentList $pnputilArgs -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\pnputil_network.log"
                Write-Log "Network driver installation completed."
            }
            catch {
                Write-Log "Error installing network drivers: $_"
            }
        } else {
            Write-Log "No INF files found in $driverPath"
        }
    } else {
        Write-Log "No network drivers folder found at $driverPath"
    }
} else {
    Write-Log "Install media not found."
}
"""

# New content for Optimize-System.ps1
optimize_system_ps1 = r"""
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-Log "Applying System Optimizations..."

# 1. Disable Hibernation (Saves disk space)
try {
    powercfg -h off
    Write-Log "Hibernation disabled."
} catch {
    Write-Log "Failed to disable hibernation: $_"
}

# 2. Set High Performance Power Plan
try {
    powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
    Write-Log "Power plan set to High Performance."
} catch {
    Write-Log "Failed to set power plan: $_"
}

# 3. Disable Game DVR (Background recording)
reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" /v AllowGameDVR /t REG_DWORD /d 0 /f

# 4. Disable Last Access Timestamp (Reduces disk I/O)
try {
    fsutil behavior set disablelastaccess 1
    Write-Log "Last Access Timestamp disabled."
} catch {
    Write-Log "Failed to disable Last Access Timestamp: $_"
}

Write-Log "System Optimizations Applied."
"""

# New content for UserOnce.ps1
user_once_ps1 = r"""
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
# Added --disable-interactivity and ensuring silent operation
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -Command `\"winget source update; winget upgrade --all --include-unknown --silent --disable-interactivity --accept-source-agreements --accept-package-agreements`\""
$trigger = New-ScheduledTaskTrigger -Daily -At 13:00
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -Hidden -RunOnlyIfNetworkAvailable
Register-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -TaskName $taskName -Description "Automatically updates all software via Winget silently." -RunLevel Highest -Force | Out-Null
Write-Log "Registered Daily Winget Auto-Update Task."

Write-Log "User Configuration Completed."

# Self-Destruct: Cleanup Scripts
# Wait 5 seconds then delete the script folder
Start-Process -FilePath "cmd.exe" -ArgumentList "/c timeout /t 5 /nobreak > NUL & rmdir /s /q `"$env:SystemRoot\Setup\Scripts`"" -WindowStyle Hidden
"""

# New content for Remove-Bloatware.ps1
remove_bloatware_ps1 = r"""
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

$packagesToRemove = @(
    'Microsoft.Microsoft3DViewer',
    'Microsoft.BingSearch',
    'Microsoft.WindowsCamera',
    'Clipchamp.Clipchamp',
    'Microsoft.WindowsAlarms',
    'Microsoft.Copilot',
    'Microsoft.Windows.DevHome',
    'MicrosoftCorporationII.MicrosoftFamily',
    'Microsoft.WindowsFeedbackHub',
    'Microsoft.GetHelp',
    'Microsoft.Getstarted',
    'microsoft.windowscommunicationsapps',
    'Microsoft.WindowsMaps',
    'Microsoft.MixedReality.Portal',
    'Microsoft.BingNews',
    'Microsoft.WindowsNotepad',
    'Microsoft.MicrosoftOfficeHub',
    'Microsoft.Office.OneNote',
    'Microsoft.OutlookForWindows',
    'Microsoft.MSPaint',
    'Microsoft.People',
    'Microsoft.Windows.Photos',
    'Microsoft.PowerAutomateDesktop',
    'MicrosoftCorporationII.QuickAssist',
    'Microsoft.SkypeApp',
    'Microsoft.MicrosoftSolitaireCollection',
    'Microsoft.MicrosoftStickyNotes',
    'MicrosoftTeams',
    'MSTeams',
    'Microsoft.Todos',
    'Microsoft.WindowsSoundRecorder',
    'Microsoft.Wallet',
    'Microsoft.BingWeather',
    'Microsoft.ZuneVideo',
    'Microsoft.Windows.Ai.Copilot.Provider',
    'Microsoft.YourPhone',
    'Microsoft.GamingApp',
    'Microsoft.XboxGameOverlay',
    'Microsoft.XboxGamingOverlay',
    'Microsoft.XboxIdentityProvider',
    'Microsoft.XboxSpeechToTextOverlay'
)

$capabilitiesToRemove = @(
    'Print.Fax.Scan',
    'Browser.InternetExplorer',
    'MathRecognizer',
    'OneCoreUAP.OneSync',
    'App.Support.QuickAssist',
    'App.StepsRecorder',
    'Hello.Face',
    'Media.WindowsMediaPlayer',
    'Microsoft.Windows.WordPad'
)

$featuresToRemove = @(
    'MediaPlayback',
    'Microsoft-RemoteDesktopConnection',
    'Recall'
)

Write-Log "Starting Debloating Process..."

# Remove Appx Provisioned Packages
$provisioned = Get-AppxProvisionedPackage -Online
foreach ($package in $packagesToRemove) {
    $found = $provisioned | Where-Object { $_.DisplayName -eq $package }
    if ($found) {
        Write-Log "Removing $package..."
        try {
            Remove-AppxProvisionedPackage -Online -PackageName $found.PackageName -ErrorAction Continue | Out-Null
        } catch {
            Write-Log "Failed to remove $package: $_"
        }
    }
}

# Remove Capabilities
$capabilities = Get-WindowsCapability -Online
foreach ($capName in $capabilitiesToRemove) {
    $cap = $capabilities | Where-Object { ($_.Name -split '~')[0] -eq $capName -and $_.State -ne 'NotPresent' }
    if ($cap) {
        Write-Log "Removing capability $capName..."
        try {
            Remove-WindowsCapability -Online -Name $cap.Name -ErrorAction Continue | Out-Null
        } catch {
            Write-Log "Failed to remove capability $capName: $_"
        }
    }
}

# Remove Optional Features
foreach ($feature in $featuresToRemove) {
    if ((Get-WindowsOptionalFeature -Online -FeatureName $feature -ErrorAction SilentlyContinue).State -eq 'Enabled') {
        Write-Log "Disabling feature $feature..."
        try {
            Disable-WindowsOptionalFeature -Online -FeatureName $feature -Remove -NoRestart -ErrorAction Continue | Out-Null
        } catch {
            Write-Log "Failed to disable feature $feature: $_"
        }
    }
}

Write-Log "Debloating Process Completed."
"""

# Apply replacements
content = replace_file_content(content, r"C:\Windows\Setup\Scripts\Lib\Helper.ps1", xml_encode(helper_ps1))
content = replace_file_content(content, r"C:\Windows\Setup\Scripts\Drivers\Install-Network.ps1", xml_encode(install_network_ps1))
content = replace_file_content(content, r"C:\Windows\Setup\Scripts\Tweaks\Optimize-System.ps1", xml_encode(optimize_system_ps1))
content = replace_file_content(content, r"C:\Windows\Setup\Scripts\UserOnce.ps1", xml_encode(user_once_ps1))
content = replace_file_content(content, r"C:\Windows\Setup\Scripts\Tweaks\Remove-Bloatware.ps1", xml_encode(remove_bloatware_ps1))

with open('autounattend.xml', 'w', encoding='utf-8') as f:
    f.write(content)

print("autounattend.xml updated successfully.")
