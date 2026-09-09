
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

# OPTIONAL: Set a direct download URL for the Focusrite Driver here.
$DownloadUrl = ""

Write-SetupLog "Starting Focusrite Driver Installation..."
$mediaRoot = Get-InstallMedia
$setupPath = $null

if ($mediaRoot) {
    $driverDir = Join-Path -Path $mediaRoot -ChildPath "drivers\focusrite"
    $setupPath = Get-InstallerFile -Path $driverDir
}

if (-not $setupPath -and $DownloadUrl) {
    $dest = "$env:TEMP\focusrite_driver.exe"
    if (Get-RemoteFile -Url $DownloadUrl -Destination $dest -Name "Focusrite Driver") {
        $setupPath = $dest
    }
}

if ($setupPath) {
    Write-SetupLog "Installing Focusrite driver from $setupPath..."
    try {
        Unblock-File -Path $setupPath -ErrorAction SilentlyContinue
        # /VERYSILENT: No UI, /SUPPRESSMSGBOXES: No popups
        Start-Process -FilePath $setupPath -ArgumentList @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/SP-') -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\focusrite_install.log"
        Write-SetupLog "Focusrite driver installation completed."
    }
    catch {
        Write-SetupLog "Error installing Focusrite drivers: $_"
    }
} else {
    Write-SetupLog "Focusrite installer not found locally and no download URL provided."
}
