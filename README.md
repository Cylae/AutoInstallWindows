# 🚀 Ultimate Windows Autounattend

This repository contains a highly optimized, modular `autounattend.xml` designed for a **silent**, **clean**, and **robust** Windows installation.

**The defining feature:** All software and driver installations occur **completely silently before the first user login**, ensuring a pristine environment the moment the desktop appears.

## ✨ Features

*   **⚡ Zero-Interruption Setup**: All software (Chrome, Drivers, etc.) is installed during the `Specialize` pass, *before* the user logs in. No popups, no waiting at the desktop.
*   **🤫 Totally Silent**: All scripts are optimized to suppress output and windows. You won't see a thing until the "Welcome" screen.
*   **🛡️ Privacy Hardened**: Disables Telemetry, Copilot, Bing Search, Cortana, and other tracking features by default.
*   **🧹 Deep Debloating**: Aggressively removes bloatware (Candy Crush, Clipchamp, etc.) and unnecessary Windows capabilities.
*   **🔧 Intelligent Driver Installation**:
    *   **Auto-Detection**: Automatically scans all drives for a `drivers` folder.
    *   **Smart Matching**: Finds installer executables (`*.exe`) automatically—no need to rename files to `setup.exe`.
    *   **Latest Nvidia Drivers**: Automatically checks Nvidia's servers and downloads the latest Game Ready Driver (DCH) if a local installer is not found.
    *   **Network Fallback**: Can attempt to download generic files from the internet if configured.
    *   **Included Support**: Scripts for Network, Nvidia GPU, AMD Chipset, and Focusrite Audio drivers.
*   **🌐 Robust App Installation**:
    *   **Offline First**: Prioritizes local installers from your USB drive (e.g., `drivers/apps/chrome`).
    *   **Internet Download**: Automatically waits for network connectivity and downloads Chrome if no local installer is found.

## 📂 Folder Structure

To utilize the offline installation features, organize your USB drive as follows:

```text
USB_ROOT/
├── autounattend.xml
└── drivers/
    ├── network/      (Place .inf files here)
    ├── nvidia/       (Place Installer .exe here)
    ├── amd/          (Place Installer .exe here)
    ├── focusrite/    (Place Installer .exe here)
    └── apps/
        └── chrome/   (Place Chrome Installer .exe here)
```

### 🌍 Internet Download

*   **Chrome**: Automatically downloads if not found locally.
*   **Nvidia**: Automatically queries Nvidia servers and downloads the latest driver if not found locally.
*   **Other Drivers**: Can be configured to download via URL in the `.ps1` scripts.

## 📝 Usage

1.  **Prepare USB**: Place `autounattend.xml` in the root of your Windows Installation Media.
2.  **Add Drivers/Apps**: Create the `drivers` folder structure and copy your installers (optional, but recommended for speed).
3.  **Boot**: Boot from the USB.
4.  **Relax**: The system will install Windows, drivers, and apps, and clean itself up automatically. When you see the desktop, it's ready.

---
---

# 🇫🇷 Ultimate Windows Autounattend (Français)

Ce dépôt contient un fichier `autounattend.xml` hautement optimisé et modulaire, conçu pour une installation Windows **silencieuse**, **propre** et **robuste**.

**La fonctionnalité clé :** Toutes les installations de logiciels et de pilotes se font **totalement silencieusement avant la première connexion utilisateur**, garantissant un environnement impeccable dès l'apparition du bureau.

## ✨ Fonctionnalités

*   **⚡ Installation Zéro-Interruption**: Tous les logiciels (Chrome, Pilotes, etc.) sont installés durant la phase `Specialize`, **avant** la connexion de l'utilisateur. Aucun popup, aucune attente sur le bureau.
*   **🤫 Totalement Silencieux**: Tous les scripts sont optimisés pour masquer les sorties et fenêtres. Vous ne verrez rien avant l'écran "Bienvenue".
*   **🛡️ Confidentialité Renforcée**: Désactive la télémétrie, Copilot, la recherche Bing, Cortana et d'autres pisteurs par défaut.
*   **🧹 Nettoyage en Profondeur**: Supprime agressivement les bloatwares (Candy Crush, Clipchamp, etc.) et les fonctionnalités Windows inutiles.
*   **🔧 Installation Intelligente des Pilotes**:
    *   **Auto-Détection**: Scanne tous les lecteurs pour trouver le dossier `drivers`.
    *   **Recherche Intelligente**: Trouve automatiquement les exécutables (`*.exe`)—pas besoin de renommer en `setup.exe`.
    *   **Derniers Pilotes Nvidia**: Vérifie automatiquement les serveurs Nvidia et télécharge le dernier pilote Game Ready (DCH) si aucun installateur local n'est trouvé.
    *   **Secours Réseau**: Peut tenter de télécharger des fichiers depuis Internet si configuré.
    *   **Support Inclus**: Scripts pour Réseau, GPU Nvidia, Chipset AMD et Audio Focusrite.
*   **🌐 Installation d'Applications Robuste**:
    *   **Hors-Ligne en Priorité**: Privilégie les installateurs locaux sur votre clé USB (ex: `drivers/apps/chrome`).
    *   **Téléchargement Internet**: Attend automatiquement la connexion réseau et télécharge Chrome si aucun installateur local n'est trouvé.

## 📂 Structure des Dossiers

Pour utiliser les fonctionnalités d'installation hors-ligne, organisez votre clé USB comme suit :

```text
RACINE_USB/
├── autounattend.xml
└── drivers/
    ├── network/      (Placez les fichiers .inf ici)
    ├── nvidia/       (Placez l'installateur .exe ici)
    ├── amd/          (Placez l'installateur .exe ici)
    ├── focusrite/    (Placez l'installateur .exe ici)
    └── apps/
        └── chrome/   (Placez l'installateur Chrome .exe ici)
```

### 🌍 Téléchargement Internet

*   **Chrome**: Télécharge automatiquement si non trouvé localement.
*   **Nvidia**: Interroge automatiquement les serveurs Nvidia et télécharge le dernier pilote si non trouvé localement.
*   **Autres Pilotes**: Peuvent être configurés pour être téléchargés via URL dans les fichiers `.ps1`.

## 📝 Utilisation

1.  **Préparer la clé USB**: Placez `autounattend.xml` à la racine de votre média d'installation Windows.
2.  **Ajouter Pilotes/Apps**: Créez la structure de dossiers `drivers` et copiez vos installateurs (optionnel, mais recommandé pour la vitesse).
3.  **Démarrer**: Démarrez sur la clé USB.
4.  **Détendez-vous**: Le système installera Windows, les pilotes et les applications, et se nettoiera automatiquement. Quand vous voyez le bureau, c'est prêt.
