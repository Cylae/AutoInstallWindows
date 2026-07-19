
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-SetupLog "Starting Visual C++ Runtimes Installation..."

$mediaRoot = Get-InstallMedia

function Install-Runtime {
    param(
        [string]$Url,
        [string]$DestName,
        [string]$LogName,
        [string]$LocalFolder
    )

    $setupPath = $null
    $dest = "$env:TEMP\$DestName"

    # 1. Try Download (Online First)
    if (Get-RemoteFile -Url $Url -Destination $dest -Name $LogName) {
        $setupPath = $dest
    }

    # 2. Try Local (Fallback)
    if (-not $setupPath -and $mediaRoot) {
        Write-SetupLog "Download of $LogName failed. Checking local storage..."
        $possiblePaths = @(
            (Join-Path $mediaRoot "apps\$LocalFolder"),
            (Join-Path $mediaRoot "drivers\apps\$LocalFolder"),
            (Join-Path $mediaRoot "Apps\$LocalFolder"),
            (Join-Path $mediaRoot "Drivers\Apps\$LocalFolder")
        )
        foreach ($path in $possiblePaths) {
             if (Test-Path $path) {
                 $localInstaller = Get-InstallerFile -Path $path
                 if ($localInstaller) {
                    $setupPath = $localInstaller
                    break
                 }
             }
        }
    }

    if ($setupPath) {
        Write-SetupLog "Installing $LogName from $setupPath..."
        try {
            Unblock-File -Path $setupPath -ErrorAction SilentlyContinue
            Start-Process -FilePath $setupPath -ArgumentList @("/install", "/quiet", "/norestart") -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\${DestName}_install.log"
            Write-SetupLog "$LogName installation completed."
        } catch {
            Write-SetupLog "Error installing $LogName: $_"
        }
    } else {
        Write-SetupLog "$LogName installer not found locally and download failed."
    }
}

# Official Microsoft Link for Latest Supported VC++ 2015-2022
$url64 = "https://aka.ms/vc14/vc_redist.x64.exe"
$url86 = "https://aka.ms/vc14/vc_redist.x86.exe"

Install-Runtime -Url $url64 -DestName "vc_redist.x64.exe" -LogName "Visual C++ Runtimes (x64)" -LocalFolder "vcredist_x64"
Install-Runtime -Url $url86 -DestName "vc_redist.x86.exe" -LogName "Visual C++ Runtimes (x86)" -LocalFolder "vcredist_x86"
