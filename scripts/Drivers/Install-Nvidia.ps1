
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

# OPTIONAL: Set a direct download URL for the Nvidia Driver here.
$DownloadUrl = ""

Write-SetupLog "Starting Nvidia Driver Installation..."
$mediaRoot = Get-InstallMedia
$setupPath = $null

# Try Local (Primary)
if ($mediaRoot) {
    Write-SetupLog "Checking local storage..."
    $driverDir = Join-Path -Path $mediaRoot -ChildPath "drivers\nvidia"
    $setupPath = Get-InstallerFile -Path $driverDir
}

# Try Download (Fallback if URL provided)
if (-not $setupPath -and $DownloadUrl) {
    $dest = "$env:TEMP\nvidia_driver.exe"
    if (Get-RemoteFile -Url $DownloadUrl -Destination $dest -Name "Nvidia Driver") {
        $setupPath = $dest
    }
}

if ($setupPath) {
    Write-SetupLog "Installing Nvidia driver from $setupPath..."
    try {
        Unblock-File -Path $setupPath -ErrorAction SilentlyContinue
        # -s: Silent, -n: No splash, -f: Force, -noreboot: No reboot
        Start-Process -FilePath $setupPath -ArgumentList @('-s', '-n', '-f', '-noreboot') -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\nvidia_install.log"
        Write-SetupLog "Nvidia driver installation completed."
    }
    catch {
        Write-SetupLog "Error installing Nvidia drivers: $_"
    }
} else {
    Write-SetupLog "Nvidia installer not found locally."
}
