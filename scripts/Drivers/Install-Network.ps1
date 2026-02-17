
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
                $pnputilArgs = "/add-driver `"$driverPath\*.inf`" /subdirs /install"
                # Redirect standard output and error to logs for debugging
                $p = Start-Process -FilePath "pnputil.exe" -ArgumentList $pnputilArgs -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\pnputil_network.log" -RedirectStandardError "$env:TEMP\pnputil_network_err.log" -PassThru

                if ($p.ExitCode -ne 0) {
                    Write-Log "pnputil failed with exit code $($p.ExitCode)"
                    if (Test-Path "$env:TEMP\pnputil_network.log") {
                        $out = Get-Content "$env:TEMP\pnputil_network.log" -Raw -ErrorAction SilentlyContinue
                        Write-Log "pnputil Output: $out"
                    }
                    if (Test-Path "$env:TEMP\pnputil_network_err.log") {
                        $err = Get-Content "$env:TEMP\pnputil_network_err.log" -Raw -ErrorAction SilentlyContinue
                        if (-not [string]::IsNullOrWhiteSpace($err)) {
                            Write-Log "pnputil Error: $err"
                        }
                    }
                } else {
                    Write-Log "Network driver installation completed successfully."
                }
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
