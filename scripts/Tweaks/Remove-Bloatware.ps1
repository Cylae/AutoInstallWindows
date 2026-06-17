$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\Lib\Helper.ps1"

$packagesToRemove = @(
    'Microsoft.Microsoft3DViewer',
    'Microsoft.BingSearch',
    'Microsoft.WindowsCamera',
    'Clipchamp.Clipchamp',
    'Microsoft.WindowsAlarms',
    'Microsoft.549981C3F5F10', # Cortana
    'Microsoft.Copilot',
    'Microsoft.Windows.DevHome',
    'MicrosoftCorporationII.MicrosoftFamily',
    'Microsoft.WindowsFeedbackHub',
    'Microsoft.GetHelp',
    'Microsoft.Getstarted',
    'microsoft.windowscommunicationsapps',
    'Microsoft.WindowsMaps',
    'Microsoft.MixedReality.Portal',
    'Microsoft.BingNews',
    'Microsoft.MicrosoftOfficeHub',
    'Microsoft.Office.OneNote',
    'Microsoft.OutlookForWindows',
    'Microsoft.People',
    'Microsoft.Windows.PeopleExperienceHost',
    'Microsoft.Windows.Photos',
    'Microsoft.PowerAutomateDesktop',
    'MicrosoftCorporationII.QuickAssist',
    'Microsoft.SkypeApp',
    'Microsoft.MicrosoftSolitaireCollection',
    'Microsoft.MicrosoftStickyNotes',
    'MicrosoftTeams',
    'MSTeams',
    'Microsoft.Todos',
    'Microsoft.WindowsSoundRecorder',
    'Microsoft.Wallet',
    'Microsoft.BingWeather',
    'Microsoft.ZuneVideo',
    'MicrosoftWindows.Client.WebExperience',
    'Microsoft.Windows.Ai.Copilot.Provider',
    'Microsoft.YourPhone',
    'Microsoft.GamingApp',
    'Microsoft.XboxGameOverlay',
    'Microsoft.XboxGamingOverlay',
    'Microsoft.XboxIdentityProvider',
    'Microsoft.XboxSpeechToTextOverlay',
    'Microsoft.Windows.ParentalControls',
    'Microsoft.BingFinance',
    'Microsoft.BingSports',
    'Microsoft.ZuneMusic',
    'Microsoft.XboxApp'
)

$packagesToKeep = @(
    'Microsoft.MSPaint',
    'Microsoft.WindowsNotepad'
)

$capabilitiesToRemove = @(
    'Print.Fax.Scan',
    'Browser.InternetExplorer',
    'MathRecognizer',
    'OneCoreUAP.OneSync',
    'App.Support.QuickAssist',
    'App.StepsRecorder',
    'Hello.Face',
    'Media.WindowsMediaPlayer',
    'Microsoft.Windows.WordPad'
)

$featuresToRemove = @(
    'MediaPlayback',
    'Microsoft-RemoteDesktopConnection',
    'Recall'
)

Write-Log "Starting Debloating Process..."

# Remove Appx Provisioned Packages
$provisioned = Get-AppxProvisionedPackage -Online
foreach ($package in $packagesToRemove) {
    $found = $provisioned | Where-Object { $_.DisplayName -eq $package -or $_.PackageName -like "*$package*" }
    if ($found) {
        foreach ($item in $found) {
            if ($packagesToKeep -contains $item.DisplayName) {
                Write-Log "Skipping preserved package $($item.DisplayName)..."
                continue
            }
            Write-Log "Removing $($item.DisplayName) ($($item.PackageName))..."
            try {
                Remove-AppxProvisionedPackage -Online -PackageName $item.PackageName -ErrorAction Continue | Out-Null
            } catch {
                Write-Log "Failed to remove $($item.PackageName): $_"
            }
        }
    }
}

# Remove Capabilities
$capabilities = Get-WindowsCapability -Online
foreach ($capName in $capabilitiesToRemove) {
    $cap = $capabilities | Where-Object { ($_.Name -split '~')[0] -eq $capName -and $_.State -ne 'NotPresent' }
    if ($cap) {
        Write-Log "Removing capability $capName..."
        try {
            Remove-WindowsCapability -Online -Name $cap.Name -ErrorAction Continue | Out-Null
        } catch {
            Write-Log "Failed to remove capability $capName: $_"
        }
    }
}

# Remove Optional Features
foreach ($feature in $featuresToRemove) {
    if ((Get-WindowsOptionalFeature -Online -FeatureName $feature -ErrorAction SilentlyContinue).State -eq 'Enabled') {
        Write-Log "Disabling feature $feature..."
        try {
            Disable-WindowsOptionalFeature -Online -FeatureName $feature -Remove -NoRestart -ErrorAction Continue | Out-Null
        } catch {
            Write-Log "Failed to disable feature $feature: $_"
        }
    }
}

Write-Log "Debloating Process Completed."
