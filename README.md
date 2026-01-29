# 🚀 Ultimate Windows Autounattend

This repository contains a highly optimized, modular `autounattend.xml` designed for a **silent**, **clean**, and **robust** Windows installation.

**The defining feature:** All software and driver installations occur **completely silently before the first user login**, ensuring a pristine environment the moment the desktop appears.

---

## ✨ Features

*   **⚡ Zero-Interruption Setup**: All software (Chrome, Drivers, etc.) is installed during the `Specialize` pass, *before* the user logs in. No popups, no waiting at the desktop.
*   **🛡️ Privacy Hardened**: Disables Telemetry, Copilot, Bing Search, Cortana, and other tracking features by default.
*   **🧹 Deep Debloating**: Aggressively removes bloatware (Candy Crush, Clipchamp, etc.) and unnecessary Windows capabilities.
*   **🔧 Intelligent Driver Installation**:
    *   **Auto-Detection**: Automatically scans all drives for a `drivers` folder.
    *   **Smart Matching**: Finds installer executables (`*.exe`) automatically—no need to rename files to `setup.exe`.
    *   **Visual Feedback**: Detailed progress logs during the setup phase.
    *   **Included Support**: Scripts for Network, Nvidia GPU, AMD Chipset, and Focusrite Audio drivers.
*   **🌐 Robust App Installation**:
    *   **Offline First**: Prioritizes local installers from your USB drive (e.g., `drivers/apps/chrome`).
    *   **Network Fallback**: Automatically waits for network connectivity and downloads Chrome if no local installer is found.

---

## 🇫🇷 Fonctionnalités (Français)

*   **⚡ Installation Zéro-Interruption**: Tous les logiciels (Chrome, Pilotes, etc.) sont installés durant la phase `Specialize`, **avant** la connexion de l'utilisateur. Aucun popup, aucune attente sur le bureau.
*   **🛡️ Confidentialité Renforcée**: Désactive la télémétrie, Copilot, la recherche Bing, Cortana et d'autres pisteurs par défaut.
*   **🧹 Nettoyage en Profondeur**: Supprime agressivement les bloatwares (Candy Crush, Clipchamp, etc.) et les fonctionnalités Windows inutiles.
*   **🔧 Installation Intelligente des Pilotes**:
    *   **Auto-Détection**: Scanne tous les lecteurs pour trouver le dossier `drivers`.
    *   **Recherche Intelligente**: Trouve automatiquement les exécutables (`*.exe`)—pas besoin de renommer en `setup.exe`.
    *   **Feedback Visuel**: Journaux de progression détaillés pendant l'installation.
    *   **Support Inclus**: Scripts pour Réseau, GPU Nvidia, Chipset AMD et Audio Focusrite.
*   **🌐 Installation d'Applications Robuste**:
    *   **Hors-Ligne en Priorité**: Privilégie les installateurs locaux sur votre clé USB (ex: `drivers/apps/chrome`).
    *   **Secours Réseau**: Attend automatiquement la connexion réseau et télécharge Chrome si aucun installateur local n'est trouvé.

---

## 📂 Folder Structure / Structure des Dossiers

To utilize the offline installation features, organize your USB drive as follows:
*Pour utiliser les fonctionnalités d'installation hors-ligne, organisez votre clé USB comme suit :*

```text
USB_ROOT/
├── autounattend.xml
└── drivers/
    ├── network/      (Place .inf files here / Placez les fichiers .inf ici)
    ├── nvidia/       (Place Installer .exe here / Placez l'installateur .exe ici)
    ├── amd/          (Place Installer .exe here / Placez l'installateur .exe ici)
    ├── focusrite/    (Place Installer .exe here / Placez l'installateur .exe ici)
    └── apps/
        └── chrome/   (Place Chrome Installer .exe here / Placez l'installateur Chrome .exe ici)
```

> **Note**: You can also place apps in `USB_ROOT/Apps` or `USB_ROOT/Drivers/Apps`. The scripts are smart enough to find them!
> **Note**: Vous pouvez aussi placer les apps dans `USB_ROOT/Apps` ou `USB_ROOT/Drivers/Apps`. Les scripts sont assez intelligents pour les trouver !

---

## 📝 Usage

1.  **Prepare USB**: Place `autounattend.xml` in the root of your Windows Installation Media.
2.  **Add Drivers/Apps**: Create the `drivers` folder structure and copy your installers.
3.  **Boot**: Boot from the USB.
4.  **Relax**: The system will install Windows, drivers, and apps, and clean itself up automatically. When you see the desktop, it's ready.

---

## 📝 Utilisation (Français)

1.  **Préparer la clé USB**: Placez `autounattend.xml` à la racine de votre média d'installation Windows.
2.  **Ajouter Pilotes/Apps**: Créez la structure de dossiers `drivers` et copiez vos installateurs.
3.  **Démarrer**: Démarrez sur la clé USB.
4.  **Détendez-vous**: Le système installera Windows, les pilotes et les applications, et se nettoiera automatiquement. Quand vous voyez le bureau, c'est prêt.
