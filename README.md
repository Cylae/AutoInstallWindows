# 🚀 Optimized Windows Autounattend

This repository contains a highly optimized `autounattend.xml` for a silent, clean, and robust Windows installation. It features improved PowerShell scripts for driver installation, debloating, and privacy configuration.

## ✨ Features

*   **🛡️ Privacy First**: Disables Telemetry, Copilot, Bing Search, and other tracking features.
*   **🧹 Debloated**: Removes bloatware apps (Candy Crush, Clipchamp, etc.) and unnecessary Windows capabilities.
*   **🔧 Robust Driver Installation**:
    *   Automatically detects installation media (USB/Drive).
    *   Installs Network drivers (`pnputil`).
    *   Installs Nvidia GPU drivers.
    *   Installs AMD Chipset drivers.
    *   Installs Focusrite Audio drivers.
*   **🌐 Chrome Installation**: Downloads and installs the latest Google Chrome.
*   **⚡ Optimized**: Scripts are modular and use efficient PowerShell techniques.

## 🇫🇷 Fonctionnalités (Français)

*   **🛡️ Confidentialité**: Désactive la télémétrie, Copilot, Bing Search et autres pisteurs.
*   **🧹 Nettoyage**: Supprime les applications préinstallées (bloatware) et fonctionnalités inutiles.
*   **🔧 Installation de Pilotes Robuste**:
    *   Détecte automatiquement le support d'installation.
    *   Installe les pilotes réseau via `pnputil`.
    *   Installe les pilotes GPU Nvidia.
    *   Installe les pilotes Chipset AMD.
    *   Installe les pilotes Audio Focusrite.
*   **🌐 Installation de Chrome**: Télécharge et installe la dernière version de Chrome.
*   **⚡ Optimisé**: Scripts modulaires et performants.

## 📂 Structure

The scripts are embedded in `autounattend.xml` and extracted to `C:\Windows\Setup\Scripts\` during installation:

*   `Lib\Helper.ps1`: Shared functions (`Get-InstallMedia`, `Write-Log`).
*   `Drivers\`: Scripts for driver installation.
*   `Apps\`: Scripts for app installation (Chrome).
*   `Tweaks\`: Scripts for debloating and privacy settings.
*   `Specialize.ps1`: Main orchestrator for the Specialize pass.
*   `FirstLogon.ps1`: Main orchestrator for the FirstLogon pass.

## 📝 Usage

1.  Place the `autounattend.xml` file in the root of your Windows Installation Media (USB).
2.  Ensure your drivers are organized in a `drivers` folder on the USB stick as follows:
    *   `drivers/network/` (Inf files)
    *   `drivers/nvidia/setup.exe`
    *   `drivers/amd/AMD_Chipset_Software.exe`
    *   `drivers/focusrite/FocusriteControl.exe`
3.  Boot from the USB and let the magic happen!
