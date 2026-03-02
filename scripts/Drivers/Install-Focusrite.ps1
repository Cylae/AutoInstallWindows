
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\..\Lib\Helper.ps1"

# OPTIONAL: Set a direct download URL for the Focusrite Driver here.
$DownloadUrl = ""

Write-Log "Starting Focusrite Driver Installation..."
$mediaRoot = Get-InstallMedia
$setupPath = $null

if ($mediaRoot) {
    $driverDir = Join-Path -Path $mediaRoot -ChildPath "drivers\focusrite"
    $setupPath = Get-InstallerFile -Path $driverDir
}

if (-not $setupPath -and $DownloadUrl) {
    $dest = "$env:TEMP\focusrite_driver.exe"
    if (Download-File -Url $DownloadUrl -Destination $dest -Name "Focusrite Driver") {
        $setupPath = $dest
    }
}

if ($setupPath) {
    Write-Log "Installing Focusrite driver from $setupPath..."
    try {
        Unblock-File -Path $setupPath -ErrorAction SilentlyContinue
        # /VERYSILENT: No UI, /SUPPRESSMSGBOXES: No popups
        Start-Process -FilePath $setupPath -ArgumentList @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/SP-') -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\focusrite_install.log" -RedirectStandardError "$env:TEMP\focusrite_install_err.log"
        if (Test-Path "$env:TEMP\focusrite_install.log") { Write-Log (Get-Content "$env:TEMP\focusrite_install.log" -Raw) }
        if (Test-Path "$env:TEMP\focusrite_install_err.log") { Write-Log (Get-Content "$env:TEMP\focusrite_install_err.log" -Raw) }
        Write-Log "Focusrite driver installation completed."
    }
    catch {
        Write-Log "Error installing Focusrite drivers: $_"
    }
} else {
    Write-Log "Focusrite installer not found locally and no download URL provided."
}
