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

    # Wait for network
    while (-not $connected -and $retry -lt $maxRetries) {
        try {
            $testHosts = @("8.8.8.8", "1.1.1.1", "google.com", "microsoft.com")
            foreach ($hostName in $testHosts) {
                try {
                    $null = [System.Net.Dns]::GetHostEntry($hostName)
                    $connected = $true
                    break
                } catch {}
            }
            if (-not $connected) { throw "No connection" }
        } catch {
            $retry++
            Start-Sleep -Seconds 2
        }
    }

    if ($connected) {
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            $userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            Invoke-WebRequest -Uri $Url -OutFile $Destination -UseBasicParsing -UserAgent $userAgent -ErrorAction Stop
            if (Test-Path -Path $Destination -And (Get-Item $Destination).Length -gt 0) {
                Write-Log "Download of $Name successful."
                return $true
            }
        } catch {
            Write-Log "Failed to download $Name: $_"
        }
    } else {
        Write-Log "No network connectivity to download $Name."
    }
    return $false
}