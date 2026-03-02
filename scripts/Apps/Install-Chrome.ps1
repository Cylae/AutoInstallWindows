
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

# 1. Try Download (Online First) - Prefer Enterprise MSI
$url = 'https://dl.google.com/chrome/install/googlechromestandaloneenterprise64.msi'
$dest = "$env:TEMP\chrome.msi"
if (Download-File -Url $url -Destination $dest -Name "Chrome Enterprise MSI") {
    $setupPath = $dest
}

# 2. Try Local (Fallback)
if (-not $setupPath -and $mediaRoot) {
    Write-Log "Download failed. Checking local storage..."
    $possiblePaths = @(
        (Join-Path $mediaRoot "apps\chrome"),
        (Join-Path $mediaRoot "drivers\apps\chrome"),
        (Join-Path $mediaRoot "Apps"),
        (Join-Path $mediaRoot "Drivers\Apps")
    )
    foreach ($path in $possiblePaths) {
         if (Test-Path $path) {
             # Prioritize MSI, then EXE
             $localInstaller = Get-InstallerFile -Path $path -Extensions @("*.msi", "*.exe")
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

        if ($setupPath -match '\.msi$') {
            # MSI Installation
            # Note: msiexec requires strict quoting for paths with spaces
            $msiArgs = @("/i", "$setupPath", "/qn", "/norestart")
            Start-Process -FilePath "msiexec.exe" -ArgumentList $msiArgs -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\chrome_install.log" -RedirectStandardError "$env:TEMP\chrome_install_err.log"
        } else {
            # EXE Installation
            Start-Process -FilePath $setupPath -ArgumentList @('/silent', '/install') -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\chrome_install.log" -RedirectStandardError "$env:TEMP\chrome_install_err.log"
        }

        if (Test-Path "$env:TEMP\chrome_install.log") { Write-Log (Get-Content "$env:TEMP\chrome_install.log" -Raw) }
        if (Test-Path "$env:TEMP\chrome_install_err.log") { Write-Log (Get-Content "$env:TEMP\chrome_install_err.log" -Raw) }

        # Cleanup temp file
        if ($setupPath -match "$env:TEMP\\chrome\.(msi|exe)") {
            Remove-Item -Path $setupPath -Force -ErrorAction SilentlyContinue
        }
        Write-Log "Chrome installation completed."
    } catch {
        Write-Log "Error installing Chrome: $_"
    }
} else {
    Write-Log "Chrome installer not found locally and download failed."
}
