# Windows Autounattend.xml Refactoring Project 🚀

## Overview ℹ️
**English:**
This project provides a highly optimized `autounattend.xml` for Windows deployment. It automates the installation of drivers (Nvidia, AMD, Focusrite, Network), removes bloatware, and applies privacy/performance tweaks. The architecture is modular, using embedded PowerShell scripts for better maintainability and error handling.

**Français:**
Ce projet fournit un fichier `autounattend.xml` hautement optimisé pour le déploiement de Windows. Il automatise l'installation des pilotes (Nvidia, AMD, Focusrite, Réseau), supprime les bloatwares et applique des ajustements de confidentialité/performance. L'architecture est modulaire, utilisant des scripts PowerShell intégrés pour une meilleure maintenance et gestion des erreurs.

## Features ✨

### 🔧 Drivers Management
- **Smart Detection:** Automatically finds the `drivers` folder on any USB drive.
- **Network:** Installs Intel/Marvell drivers automatically (`pnputil`).
- **GPU:** Silent installation for Nvidia and AMD chipsets.
- **Audio:** Silent installation for Focusrite Control.

### 🧹 Debloating & Optimization
- **Bloatware Removal:** Removes over 30+ built-in apps (Candy Crush, Solitaire, etc.).
- **Privacy:** Disables Telemetry, Copilot, Recall, and "News and Interests".
- **Performance:** Disables VBS (Virtualization Based Security), Startup Boost, and background apps.

### 👤 User Experience
- **Taskbar:** Left-aligned, no search box, no "Task View" button.
- **Explorer:** Launches to "This PC", classic context menu tweaks.
- **Start Menu:** Clean slate (no pinned ads).
- **Chrome:** Auto-download and silent install.

## Change Log 📝

### Refactoring
- **Modular Scripts:** Consolidated 15+ fragmented scripts into 4 robust modules (`Install-Drivers.ps1`, `Optimize-OS.ps1`, `Configure-User.ps1`, `Global-Functions.ps1`).
- **Error Handling:** Added `try/catch` blocks and logging to `C:\Windows\Setup\Scripts\*.log`.
- **Visual Feedback:** Implemented `Write-Progress` to show status bars during Windows Setup.

### Improvements
- **Idempotency:** Scripts check if drivers/keys exist before acting, preventing errors.
- **Security:** Added strict `TLS 1.2` enforcement for Chrome download.
- **Registry:** Added missing keys for Notepad (Old context menu), Explorer policies, and Account/Password policies.
- **Cleanliness:** Auto-removes `OneDriveSetup.exe` and cleanup scripts after execution.

## How to Use 🛠️
1. Place `autounattend.xml` in the root of your USB drive.
2. Ensure your USB drive has a `drivers` folder with the following structure:
   ```
   drivers/
   ├── amd/
   ├── focusrite/
   ├── network/
   └── nvidia/
   ```
3. Boot from the USB to start the unattended installation.

---
*Optimized by Jules*
