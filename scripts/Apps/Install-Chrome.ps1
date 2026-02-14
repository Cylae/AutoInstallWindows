
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-Log "Starting Chrome Installation..."

# Check if Chrome is already installed
if ((Test-Path "$env:ProgramFiles\Google\Chrome\Application\chrome.exe") -or (Test-Path "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe")) {
    Write-Log "Chrome is already installed. Skipping."
    return
}

$mediaRoot = Get-InstallMedia
$setupPath = $null

# 1. Try Download (Online First) - Prefer Enterprise MSI for silent install
# Use the stable Enterprise MSI link
$url = 'https://dl.google.com/tag/s/appguid%3D%7B8A69D345-D564-463C-AFF1-A69D9E530F96%7D%26iid%3D%7BBA652416-577E-2821-8273-030291916362%7D%26lang%3Den%26browser%3D3%26usagestats%3D0%26appname%3DGoogle%2520Chrome%26needsadmin%3Dtrue%26ap%3Dx64-stable-statsdef_1/dl/chrome/install/googlechromestandaloneenterprise64.msi'
$dest = "$env:TEMP\chrome.msi"
if (Download-File -Url $url -Destination $dest -Name "Chrome Enterprise MSI") {
    $setupPath = $dest
}

# 2. Try Local (Fallback)
if (-not $setupPath -and $mediaRoot) {
    Write-Log "Download failed. Checking local storage..."
    $possiblePaths = @(
        (Join-Path $mediaRoot "apps\chrome"),
        (Join-Path $mediaRoot "drivers\apps\chrome"),
        (Join-Path $mediaRoot "Apps"),
        (Join-Path $mediaRoot "Drivers\Apps")
    )
    foreach ($path in $possiblePaths) {
         if (Test-Path $path) {
             # Check for MSI first, then EXE
             $localMsi = Get-ChildItem -Path $path -Filter "*.msi" | Select-Object -First 1
             if ($localMsi) {
                 $setupPath = $localMsi.FullName
                 break
             }
             $localExe = Get-InstallerFile -Path $path
             if ($localExe) {
                $setupPath = $localExe
                break
             }
         }
    }
}

if ($setupPath) {
    Write-Log "Installing Chrome from $setupPath..."
    try {
        Unblock-File -Path $setupPath -ErrorAction SilentlyContinue

        if ($setupPath.EndsWith(".msi", [System.StringComparison]::OrdinalIgnoreCase)) {
            # MSI Installation
            Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$setupPath`" /qn /norestart" -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\chrome_install.log"
        } else {
            # EXE Installation
            Start-Process -FilePath $setupPath -ArgumentList '/silent /install' -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\chrome_install.log"
        }

        if ($setupPath -eq "$env:TEMP\chrome.msi") {
            Remove-Item -Path $setupPath -Force -ErrorAction SilentlyContinue
        }
        Write-Log "Chrome installation completed."
    } catch {
        Write-Log "Error installing Chrome: $_"
    }
} else {
    Write-Log "Chrome installer not found locally and download failed."
}
