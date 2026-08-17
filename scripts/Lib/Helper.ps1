function Get-InstallMedia {
    # Use .NET DriveInfo to correctly identify Fixed/Removable drives and avoid network/floppy hangs
    $drives = [System.IO.DriveInfo]::GetDrives() | Where-Object { $_.DriveType -in 'Fixed', 'Removable' -and $_.IsReady }
    foreach ($drive in $drives) {
        $path = Join-Path -Path $drive.RootDirectory.FullName -ChildPath "drivers"
        if (Test-Path -Path $path -PathType Container) {
            return $drive.RootDirectory.FullName
        }
    }
    return $null
}

function Get-InstallerFile {
    param([string]$Path, [string[]]$Extensions = @("*.exe"))
    if (Test-Path -Path $Path) {
        foreach ($ext in $Extensions) {
            $file = Get-ChildItem -Path $Path -Filter $ext | Select-Object -First 1
            if ($file) { return $file.FullName }
        }
    }
    return $null
}

function Write-SetupLog {
    param(
        [string]$Message,
        [string]$Path = "$env:SystemRoot\Panther\Autounattend_Log.txt"
    )
    # Ensure directory exists
    $dir = Split-Path -Path $Path -Parent
    if (-not (Test-Path -Path $dir)) {
        New-Item -Path $dir -ItemType Directory -Force -ErrorAction SilentlyContinue | Out-Null
    }

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $logEntry = "[$timestamp] $Message"
    Add-Content -Path $Path -Value $logEntry -ErrorAction SilentlyContinue
}

function Get-RemoteFile {
    param(
        [string]$Url,
        [string]$Destination,
        [string]$Name = "File"
    )

    # Suppress Progress Bar for Faster Download
    $ProgressPreference = 'SilentlyContinue'

    if ([string]::IsNullOrWhiteSpace($Url)) { return $false }

    Write-SetupLog "Attempting to download $Name from $Url..."

    # Increase timeout to ~5 minutes (150 * 2s) to handle slow network initialization
    $maxRetries = 150
    $retry = 0
    $connected = $false

    # Wait for network
    while (-not $connected -and $retry -lt $maxRetries) {
        $testHosts = @("google.com", "microsoft.com", "cloudflare.com")
        foreach ($hostName in $testHosts) {
            try {
                $null = [System.Net.Dns]::GetHostEntry($hostName)
                $connected = $true
                break
            } catch {}
        }

        if (-not $connected) {
            $retry++
            Start-Sleep -Seconds 2
        }
    }

    if (-not $connected) {
        Write-SetupLog "No network connectivity to download $Name."
        return $false
    }

    $downloadRetries = 5
    $dRetry = 0
    $downloaded = $false

    while (-not $downloaded -and $dRetry -lt $downloadRetries) {
        try {
            # Enable TLS 1.2 and TLS 1.3 (if available)
            $protocols = [Net.SecurityProtocolType]::Tls12
            try { $protocols = $protocols -bor [Net.SecurityProtocolType]::Tls13 } catch {}
            [Net.ServicePointManager]::SecurityProtocol = $protocols

            Invoke-WebRequest -Uri $Url -OutFile $Destination -UseBasicParsing -ErrorAction Stop

            # Verify file size > 1KB (1024 bytes) to ensure valid download
            if (Test-Path -Path $Destination -And (Get-Item $Destination).Length -gt 1024) {
                Write-SetupLog "Download of $Name successful."
                $downloaded = $true
            } else {
                Write-SetupLog "Download of $Name failed (file too small or empty)."
                throw "File too small"
            }
        } catch {
            $dRetry++
            Write-SetupLog "Failed to download $Name (Attempt $dRetry/$downloadRetries): $_"
            Start-Sleep -Seconds 5
        }
    }

    return $downloaded
}

function Set-RegistryKey {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][AllowEmptyString()][string]$Name,
        [Parameter(Mandatory=$true)][AllowEmptyString()]$Value,
        [Parameter(Mandatory=$true)][string]$Type
    )

    # Map HKU to Registry::HKEY_USERS for DefaultUser.ps1 compatibility
    if ($Path -match "^HKU\\(.*)") {
        $Path = "Registry::HKEY_USERS\" + $matches[1]
    }
    elseif ($Path -match "^HKEY_USERS\\(.*)") {
        $Path = "Registry::HKEY_USERS\" + $matches[1]
    }

    $PathParts = $Path -split "\\"
    $CurrentPath = $PathParts[0]

    # Handle the root properly if it is a PSDrive (ends with :) or Registry:: prefix
    if (-not ($CurrentPath -match ":$") -and -not ($CurrentPath -match "^Registry::")) {
        $CurrentPath = $CurrentPath + ":"
    }

    for ($i = 1; $i -lt $PathParts.Length; $i++) {
        $CurrentPath = Join-Path $CurrentPath $PathParts[$i]
        if (-not (Test-Path -LiteralPath $CurrentPath)) {
            New-Item -Path ($CurrentPath -replace "\\[^\\]+$", "") -Name $PathParts[$i] -Force | Out-Null
        }
    }

    if ($Name -eq "") {
        Set-Item -LiteralPath $Path -Value $Value -Force | Out-Null
    } else {
        Set-ItemProperty -LiteralPath $Path -Name $Name -Value $Value -Type $Type -Force | Out-Null
    }
}
