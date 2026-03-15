
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\..\Lib\Helper.ps1"

Write-Log "Starting Network Driver Installation..."
$mediaRoot = Get-InstallMedia

if ($mediaRoot) {
    $driverPath = Join-Path -Path $mediaRoot -ChildPath "drivers\network"
    if (Test-Path -Path $driverPath) {
        Write-Log "Found network drivers path at $driverPath"
        # Check if there are any INF files to avoid pnputil error
        if (Get-ChildItem -Path $driverPath -Filter "*.inf" -Recurse) {
            try {
                $pnputilArgs = @("/add-driver", "$driverPath\*.inf", "/subdirs", "/install")
                # Redirect standard output and error to logs for debugging
                Start-Process -FilePath "pnputil.exe" -ArgumentList $pnputilArgs -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\pnputil_network.log" -RedirectStandardError "$env:TEMP\pnputil_network_err.log"
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
