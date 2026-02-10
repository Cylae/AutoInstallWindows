$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

# OPTIONAL: Set a direct download URL for the AMD Chipset Driver here.
$DownloadUrl = ""

Write-Log "Starting AMD Chipset Driver Installation..."
$mediaRoot = Get-InstallMedia
$setupPath = $null

if ($mediaRoot) {
    $driverDir = Join-Path -Path $mediaRoot -ChildPath "drivers\amd"
    $setupPath = Get-InstallerFile -Path $driverDir
}

if (-not $setupPath -and $DownloadUrl) {
    $dest = "$env:TEMP\amd_chipset.exe"
    if (Download-File -Url $DownloadUrl -Destination $dest -Name "AMD Chipset") {
        $setupPath = $dest
    }
}

if ($setupPath) {
    Write-Log "Installing AMD driver from $setupPath..."
    try {
        Unblock-File -Path $setupPath -ErrorAction SilentlyContinue
        # /S: Silent
        Start-Process -FilePath $setupPath -ArgumentList "/S", "-noreboot" -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\amd_install.log"
        Write-Log "AMD Chipset driver installation completed."
    }
    catch {
        Write-Log "Error installing AMD Chipset drivers: $_"
    }
} else {
    Write-Log "AMD installer not found locally and no download URL provided."
}