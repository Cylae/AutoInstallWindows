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
        [string]$Path,
        [string]$Name,
        [string]$Value,
        [string]$Type = "String"
    )

    # Handle reg.exe style hives
    $psPath = $Path -replace "^HKLM\\", "HKLM:\" `
                    -replace "^HKCU\\", "HKCU:\" `
                    -replace "^HKU\\", "Registry::HKEY_USERS\" `
                    -replace "^HKEY_USERS\\", "Registry::HKEY_USERS\" `
                    -replace "^HKCR\\", "HKCR:\" `
                    -replace "^HKCC\\", "HKCC:\"

    # Create parent keys if they don't exist
    if (-not (Test-Path -Path $psPath)) {
        $pathParts = $psPath -split "\\"
        $currentPath = $pathParts[0]
        for ($i = 1; $i -lt $pathParts.Count; $i++) {
            $currentPath = Join-Path -Path $currentPath -ChildPath $pathParts[$i]
            if (-not (Test-Path -Path $currentPath)) {
                New-Item -Path $currentPath -Force -ErrorAction SilentlyContinue | Out-Null
            }
        }
    }

    # Set value
    if ([string]::IsNullOrEmpty($Name) -or $Name -eq "(default)") {
        Set-Item -Path $psPath -Value $Value -Force -ErrorAction SilentlyContinue | Out-Null
    } else {
        Set-ItemProperty -Path $psPath -Name $Name -Value $Value -Type $Type -Force -ErrorAction SilentlyContinue | Out-Null
    }
}
