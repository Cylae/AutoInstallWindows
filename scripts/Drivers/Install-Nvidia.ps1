
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-Log "Starting Nvidia Driver Installation..."
$mediaRoot = Get-InstallMedia
$setupPath = $null

# Online check removed due to API deprecation.
# To use a direct download, set the URL below manually or use the local drivers folder.
# $url = "https://..."

# Try Local (Fallback/Primary)
if (-not $setupPath -and $mediaRoot) {
    Write-Log "Checking local storage..."
    $driverDir = Join-Path -Path $mediaRoot -ChildPath "drivers\nvidia"
    $setupPath = Get-InstallerFile -Path $driverDir
}

if ($setupPath) {
    Write-Log "Installing Nvidia driver from $setupPath..."
    try {
        Unblock-File -Path $setupPath -ErrorAction SilentlyContinue
        # -s: Silent, -n: No splash, -f: Force, -noreboot: No reboot
        Start-Process -FilePath $setupPath -ArgumentList @('-s', '-n', '-f', '-noreboot') -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\nvidia_install.log"
        Write-Log "Nvidia driver installation completed."
    }
    catch {
        Write-Log "Error installing Nvidia drivers: $_"
    }
} else {
    Write-Log "Nvidia installer not found locally."
}
