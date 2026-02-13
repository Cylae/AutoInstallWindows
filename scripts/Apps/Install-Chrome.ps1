
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\..\Lib\Helper.ps1"

Write-Log "Starting Chrome Installation..."

# Check if Chrome is already installed
if ((Test-Path "$env:ProgramFiles\Google\Chrome\Application\chrome.exe") -or (Test-Path "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe")) {
    Write-Log "Chrome is already installed. Skipping."
    return
}

$mediaRoot = Get-InstallMedia
$setupPath = $null

# 1. Try Download (Online First)
$url = 'https://dl.google.com/chrome/install/chrome_installer.exe'
$dest = "$env:TEMP\chrome.exe"
# Download-File handles connectivity checks and retries
if (Download-File -Url $url -Destination $dest -Name "Chrome") {
    $setupPath = $dest
}

# 2. Try Local (Fallback)
if (-not $setupPath -and $mediaRoot) {
    Write-Log "Download failed or skipped. Checking local storage..."
    $possiblePaths = @(
        (Join-Path $mediaRoot "apps\chrome"),
        (Join-Path $mediaRoot "drivers\apps\chrome"),
        (Join-Path $mediaRoot "Apps"),
        (Join-Path $mediaRoot "Drivers\Apps")
    )
    foreach ($path in $possiblePaths) {
         if (Test-Path $path) {
             $localInstaller = Get-InstallerFile -Path $path
             if ($localInstaller) {
                $setupPath = $localInstaller
                break
             }
         }
    }
}

if ($setupPath) {
    Write-Log "Installing Chrome from $setupPath..."
    try {
        Unblock-File -Path $setupPath -ErrorAction SilentlyContinue
        Start-Process -FilePath $setupPath -ArgumentList '/silent /install' -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\chrome_install.log"
        Write-Log "Chrome installation completed."
    } catch {
        Write-Log "Error installing Chrome: $_"
    } finally {
        # Cleanup downloaded file
        if ($setupPath -eq "$env:TEMP\chrome.exe") {
            Remove-Item -Path $setupPath -Force -ErrorAction SilentlyContinue
        }
    }
} else {
    Write-Log "Chrome installer not found locally and download failed."
}
