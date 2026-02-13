function Get-InstallMedia {
    $drives = Get-PSDrive -PSProvider FileSystem
    foreach ($drive in $drives) {
        $path = Join-Path -Path $drive.Root -ChildPath "drivers"
        if (Test-Path -Path $path -PathType Container) {
            return $drive.Root
        }
    }
    return $null
}

function Get-InstallerFile {
    param([string]$Path)
    if (Test-Path -Path $Path) {
        $file = Get-ChildItem -Path $Path -Filter "*.exe" | Select-Object -First 1
        if ($file) { return $file.FullName }
    }
    return $null
}

function Write-Log {
    param(
        [string]$Message,
        [string]$Path = "$env:SystemRoot\Panther\Autounattend_Log.txt"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Add-Content -Path $Path -Value $logEntry -ErrorAction SilentlyContinue
    # Write-Host is useful for debugging but we want total silence in production
    # Write-Host $logEntry
}

function Download-File {
    param(
        [string]$Url,
        [string]$Destination,
        [string]$Name = "File"
    )

    if ([string]::IsNullOrWhiteSpace($Url)) { return $false }

    Write-Log "Attempting to download $Name from $Url..."

    # Increase timeout to ~5 minutes (150 * 2s) to handle slow network initialization
    $maxRetries = 150
    $retry = 0
    $connected = $false

    # Suppress progress bar for speed
    $ProgressPreference = 'SilentlyContinue'

    # Wait for network
    while (-not $connected -and $retry -lt $maxRetries) {
        try {
            # Try to reach reliable hosts via HTTP to verify actual internet access
            $testHosts = @("http://www.google.com", "http://www.microsoft.com", "http://1.1.1.1")
            foreach ($host in $testHosts) {
                try {
                    $response = Invoke-WebRequest -Uri $host -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
                    if ($response.StatusCode -eq 200) {
                        $connected = $true
                        break
                    }
                } catch {}
            }
            if (-not $connected) { throw "No connection" }
        } catch {
            $retry++
            Start-Sleep -Seconds 2
        }
    }

    if (-not $connected) {
        Write-Log "No network connectivity to download $Name."
        return $false
    }

    $downloadRetries = 3
    $dRetry = 0
    $downloaded = $false

    while (-not $downloaded -and $dRetry -lt $downloadRetries) {
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            # 10 minute timeout for large files
            Invoke-WebRequest -Uri $Url -OutFile $Destination -UseBasicParsing -TimeoutSec 600 -ErrorAction Stop

            # Verify file size > 1KB (1024 bytes) to ensure valid download
            if (Test-Path -Path $Destination -And (Get-Item $Destination).Length -gt 1024) {
                Write-Log "Download of $Name successful."
                $downloaded = $true
            } else {
                Write-Log "Download of $Name failed (file too small or empty)."
                throw "File too small"
            }
        } catch {
            $dRetry++
            Write-Log "Failed to download $Name (Attempt $dRetry/$downloadRetries): $_"
            Start-Sleep -Seconds 2
        }
    }

    return $downloaded
}
