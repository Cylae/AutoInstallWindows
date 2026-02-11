# Change Log

## [Fixes & Enhancements] - 2024-05-25

### 🚀 Enhancements
*   **Robust Networking**: Completely rewrote `Download-File` helper with robust retry logic for both connectivity checks and file downloads.
*   **User Experience**: Disabled "Finish setting up your device" and "Lock Screen Tips" prompts.
*   **Chrome Install**: Added idempotency check to skip installation if Chrome is already present.

### 🧹 Debloating
*   **Expanded Removal**: Added Cortana (`Microsoft.549981C3F5F10`), PeopleExperienceHost, and ParentalControls to the bloatware removal list.

## [Fixes & Enhancements] - 2024-05-24

### 🚀 Enhancements
*   **Log Persistence**: Changed log file location to `C:\Windows\Panther\Autounattend_Log.txt` so it is preserved after cleanup.
*   **System Optimization**: Added `fsutil behavior set disablelastaccess 1` to improve file system performance.
*   **Winget**: Added `--disable-interactivity` to the daily auto-update task to prevent potential hangs.

### 🧹 Debloating
*   **Your Phone**: Added `Microsoft.YourPhone` to the removal list.

## [Refactoring] - 2024-05-23

### 🚀 Performance & Robustness
*   **Driver Detection**: Replaced fragile drive letter assumptions with a robust `Get-InstallMedia` function that scans all drives for the `drivers` folder.
*   **Modular Scripts**: Split monolithic logic into dedicated scripts (`Install-Network.ps1`, `Install-Nvidia.ps1`, etc.) for better maintainability and error isolation.
*   **Debloating**: Consolidated multiple removal passes into a single `Remove-Bloatware.ps1` script, optimizing execution time.
*   **Chrome Install**: Added basic parsing and error handling to the Chrome download process.

### 🛡️ Privacy & Security
*   **Enhanced Tweaks**: Added registry keys to disable Windows Copilot, Edge "First Run" experience, and more telemetry points.
*   **Security**: Ensured `EnableVirtualizationBasedSecurity` is explicitly disabled (as requested for performance/compatibility) via registry.

### 🐛 Bug Fixes
*   Fixed potential issues where scripts would fail if the USB drive letter changed between passes.
*   Added `try/catch` blocks around critical operations (driver installs, downloads) to prevent the setup from hanging or failing silently.
*   Added `Write-Log` function to creating a persistent log file at `C:\Windows\Setup\Scripts\Setup.log` for troubleshooting.

### 🎨 Visual Feedback
*   Retained `Write-Progress` but with clearer messages during the installation process.
