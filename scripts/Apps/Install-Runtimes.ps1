$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

Write-Log "Starting Visual C++ Runtimes Installation..."

# Official Microsoft Link for Latest Supported VC++ 2015-2022
$url64 = "https://aka.ms/vc14/vc_redist.x64.exe"
$url86 = "https://aka.ms/vc14/vc_redist.x86.exe"

$dest64 = "$env:TEMP\vc_redist.x64.exe"
$dest86 = "$env:TEMP\vc_redist.x86.exe"

# Install x64
if (Download-File -Url $url64 -Destination $dest64 -Name "Visual C++ Runtimes (x64)") {
    Write-Log "Installing Visual C++ Runtimes (x64)..."
    try {
        Unblock-File -Path $dest64 -ErrorAction SilentlyContinue
        Start-Process -FilePath $dest64 -ArgumentList "/install /quiet /norestart" -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\vcredist_x64_install.log"
        Write-Log "Visual C++ Runtimes (x64) installation completed."
    } catch {
        Write-Log "Error installing Visual C++ Runtimes (x64): $_"
    }
} else {
    Write-Log "Failed to download Visual C++ Runtimes (x64)."
}

# Install x86
if (Download-File -Url $url86 -Destination $dest86 -Name "Visual C++ Runtimes (x86)") {
    Write-Log "Installing Visual C++ Runtimes (x86)..."
    try {
        Unblock-File -Path $dest86 -ErrorAction SilentlyContinue
        Start-Process -FilePath $dest86 -ArgumentList "/install /quiet /norestart" -Wait -NoNewWindow -RedirectStandardOutput "$env:TEMP\vcredist_x86_install.log"
        Write-Log "Visual C++ Runtimes (x86) installation completed."
    } catch {
        Write-Log "Error installing Visual C++ Runtimes (x86): $_"
    }
} else {
    Write-Log "Failed to download Visual C++ Runtimes (x86)."
}