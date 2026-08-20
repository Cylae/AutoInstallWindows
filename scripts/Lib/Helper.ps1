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
            } catch { $_ | Out-Null }
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
            try { $protocols = $protocols -bor [Net.SecurityProtocolType]::Tls13 } catch { $_ | Out-Null }
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
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path,
        [Parameter(Mandatory=$true)]
        [AllowEmptyString()]
        [string]$Name,
        [Parameter(Mandatory=$true)]
        [AllowEmptyString()]
        $Value,
        [Parameter(Mandatory=$false)]
        [string]$Type = "String"
    )

    # Convert common prefixes to PSDrive paths safely
    if ($Path -match "^HKLM\\") {
        $Path = $Path -replace "^HKLM\\", "HKLM:\"
    } elseif ($Path -match "^HKCU\\") {
        $Path = $Path -replace "^HKCU\\", "HKCU:\"
    } elseif ($Path -match "^HKU\\") {
        $Path = $Path -replace "^HKU\\", "Registry::HKEY_USERS\"
    } elseif ($Path -match "^HKEY_USERS\\") {
        $Path = $Path -replace "^HKEY_USERS\\", "Registry::HKEY_USERS\"
    }

    # Split the path to recursively create keys if they don't exist
    $pathParts = $Path -split "\\"
    $parentPath = $pathParts[0]

    # Ensure the root has a trailing slash for provider root (like HKLM:)
    if ($parentPath -match ':$' -or $parentPath -match '^Registry::') {
        if (-not ($parentPath.EndsWith('\') -or $parentPath.EndsWith(':'))) {
            # Usually provider paths are fine, let's just make sure it's constructed correctly
        }
    } else {
        Write-Warning "Unrecognized registry root: $parentPath"
        return
    }

    for ($i = 1; $i -lt $pathParts.Count; $i++) {
        $childPath = $pathParts[$i]
        $currentPath = Join-Path $parentPath $childPath

        # Test-Path fails with wildcard issues if brackets are in the path (like CLSIDs). Use -LiteralPath.
        if (-not (Test-Path -LiteralPath $currentPath)) {
            New-Item -LiteralPath $parentPath -Name $childPath -Force | Out-Null
        }
        $parentPath = $currentPath
    }

    if ($Name -eq "") {
        # Set the (default) value
        Set-Item -LiteralPath $Path -Value $Value | Out-Null
    } else {
        Set-ItemProperty -LiteralPath $Path -Name $Name -Value $Value -Type $Type -Force | Out-Null
    }
}
