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

function Write-Log {
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

function Download-File {
    param(
        [string]$Url,
        [string]$Destination,
        [string]$Name = "File"
    )

    # Suppress Progress Bar for Faster Download
    $ProgressPreference = 'SilentlyContinue'

    if ([string]::IsNullOrWhiteSpace($Url)) { return $false }

    Write-Log "Attempting to download $Name from $Url..."

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
        Write-Log "No network connectivity to download $Name."
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
                Write-Log "Download of $Name successful."
                $downloaded = $true
            } else {
                Write-Log "Download of $Name failed (file too small or empty)."
                throw "File too small"
            }
        } catch {
            $dRetry++
            Write-Log "Failed to download $Name (Attempt $dRetry/$downloadRetries): $_"
            Start-Sleep -Seconds 5
        }
    }

    return $downloaded
}

function Set-RegistryKey {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path,
        [Parameter(Mandatory=$true)]
        [string]$Name,
        [Parameter(Mandatory=$true)]
        [string]$Value,
        [Parameter(Mandatory=$true)]
        [string]$Type
    )

    # Convert paths starting with HKLM\ or HKU\ to PowerShell drives if they aren't already
    $psPath = $Path
    if ($psPath -match "^HKLM\\") {
        $psPath = $psPath -replace "^HKLM\\", "HKLM:\"
    } elseif ($psPath -match "^HKU\\") {
        $psPath = $psPath -replace "^HKU\\", "Registry::HKEY_USERS\"
    } elseif ($psPath -match "^HKEY_USERS\\") {
        $psPath = $psPath -replace "^HKEY_USERS\\", "Registry::HKEY_USERS\"
    }

    # Split the path into parts to recursively create parent keys if they don't exist
    # If using a PS drive, the first part is the drive (e.g. "HKLM:")
    $parts = $psPath -split "\\"
    $currentPath = ""

    foreach ($part in $parts) {
        if ([string]::IsNullOrEmpty($currentPath)) {
            $currentPath = $part
        } else {
            $currentPath = "$currentPath\$part"
        }

        # Test-Path doesn't work well if path has wildcards unless -LiteralPath is used
        if (-not (Test-Path -LiteralPath $currentPath)) {
            try {
                # New-Item needs the parent path and the new name
                $parentPath = Split-Path -Path $currentPath -Parent
                $childName = Split-Path -Path $currentPath -Leaf
                New-Item -Path $parentPath -Name $childName -Force -ErrorAction Stop | Out-Null
            } catch {
                Write-Log "Failed to create registry path: $currentPath"
            }
        }
    }

    try {
        if ($Name -eq "") {
            Set-Item -LiteralPath $psPath -Value $Value -Force -ErrorAction Stop
        } else {
            Set-ItemProperty -LiteralPath $psPath -Name $Name -Value $Value -Type $Type -Force -ErrorAction Stop
        }
    } catch {
        Write-Log "Failed to set registry value $Name at $psPath"
    }
}
