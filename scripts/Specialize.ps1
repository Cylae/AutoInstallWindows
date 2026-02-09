
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

$scripts = @(
    "$PSScriptRoot\Drivers\Install-Network.ps1",
    "$PSScriptRoot\Tweaks\Remove-Bloatware.ps1",
    "$PSScriptRoot\Tweaks\Configure-Privacy.ps1",
    "$PSScriptRoot\Tweaks\Optimize-System.ps1",
    "$PSScriptRoot\Drivers\Install-Nvidia.ps1",
    "$PSScriptRoot\Drivers\Install-AMD.ps1",
    "$PSScriptRoot\Drivers\Install-Focusrite.ps1",
    "$PSScriptRoot\Apps\Install-Runtimes.ps1",
    "$PSScriptRoot\Apps\Install-Chrome.ps1",
    "$PSScriptRoot\Tweaks\SetStartPins.ps1"
)

Write-Log "Starting Specialize Pass (Optimized)..."

foreach ($script in $scripts) {
    if (Test-Path $script) {
        Write-Log "Executing $script..."
        try {
            & $script
        } catch {
            Write-Log "Error executing $script: $_"
        }
    } else {
        Write-Log "Script not found: $script"
    }
}

# Generate SetupComplete.cmd for post-OOBE cleanup
# This ensures unattend.xml remains available for OOBE but is removed before login
$setupCompleteContent = @"
del /q /f "%WINDIR%\Panther\unattend.xml"
del /q /f "%WINDIR%\Panther\unattend-original.xml"
"@

$setupCompletePath = "$env:SystemRoot\Setup\Scripts\SetupComplete.cmd"
try {
    Set-Content -Path $setupCompletePath -Value $setupCompleteContent -Force
    Write-Log "Generated SetupComplete.cmd for cleanup."
} catch {
    Write-Log "Error creating SetupComplete.cmd: $_"
}

Write-Log "Specialize Pass Completed."

