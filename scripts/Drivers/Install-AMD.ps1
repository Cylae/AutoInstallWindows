
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

# OPTIONAL: Set a direct download URL for the AMD Chipset Driver here.
$DownloadUrl = ""

Write-SetupLog "Starting AMD Chipset Driver Installation..."
$mediaRoot = Get-InstallMedia
$setupPath = $null

if ($mediaRoot) {
    $driverDir = Join-Path -Path $mediaRoot -ChildPath "drivers\amd"
    $setupPath = Get-InstallerFile -Path $driverDir
}

if (-not $setupPath -and $DownloadUrl) {
    $dest = "$env:TEMP\amd_chipset.exe"
    if (Get-RemoteFile -Url $DownloadUrl -Destination $dest -Name "AMD Chipset") {
        $setupPath = $dest
    }
}

if ($setupPath) {
    Write-SetupLog "Installing AMD driver from $setupPath..."
    try {
        Unblock-File -Path $setupPath -ErrorAction SilentlyContinue
        # /S: Silent
        Start-Process -FilePath $setupPath -ArgumentList "/S", "-noreboot" -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\amd_install.log"
        Write-SetupLog "AMD Chipset driver installation completed."
    }
    catch {
        Write-SetupLog "Error installing AMD Chipset drivers: $_"
    }
} else {
    Write-SetupLog "AMD installer not found locally and no download URL provided."
}
