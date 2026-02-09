# 🚀 Ultimate Windows Autounattend

This repository contains a highly optimized, modular `autounattend.xml` designed for a **silent**, **clean**, and **robust** Windows installation.

**The defining feature:** All software and driver installations occur **completely silently before the first user login**, ensuring a pristine environment the moment the desktop appears.

## ✨ Features

*   **⚡ Zero-Interruption Setup**: All software (Chrome, Drivers, etc.) is installed during the `Specialize` pass, *before* the user logs in. No popups, no waiting at the desktop.
*   **🤫 Totally Silent**: All scripts are optimized to suppress output and windows. You won't see a thing until the "Welcome" screen.
*   **🛡️ Privacy Hardened**: Disables Telemetry, Copilot, Bing Search, Cortana, Advertising ID, Search Highlights. **Restores Classic Context Menu** (Windows 11) and shows file extensions by default.
*   **🌑 Dark Mode**: Enables Dark Mode for System and Apps by default.
*   **🧹 Deep Debloating**: Aggressively removes bloatware (Candy Crush, Clipchamp, Phone Link, etc.) and unnecessary Windows capabilities.
*   **💥 Self-Destruct**: Installation scripts automatically delete themselves after the first login to ensure a clean slate.
*   **📜 Log Persistence**: Setup logs are preserved in `C:\Windows\Panther\Autounattend_Log.txt` for troubleshooting.
*   **🚀 System Optimization**:
    *   **High Performance**: Automatically sets the "High Performance" power plan.
    *   **Power User**: Enables "End Task" in Taskbar context menu.
    *   **Space Saving**: Disables Hibernation to save disk space (`hiberfil.sys`).
    *   **Gaming**: Disables Game DVR/Bar for better gaming performance.
    *   **IO**: Disables "Last Access" timestamp updates for better file system performance.
*   **🔧 Intelligent Driver Installation**:
    *   **Auto-Detection**: Automatically scans all drives for a `drivers` folder.
    *   **Smart Matching**: Finds installer executables (`*.exe`) automatically—no need to rename files to `setup.exe`.
    *   **Included Support**: Scripts for Network, Nvidia GPU, AMD Chipset, and Focusrite Audio drivers.
*   **🌐 Robust App Installation**:
    *   **Smart Connectivity**: Verified internet checks against multiple reliable hosts (Google, Cloudflare, Microsoft).
    *   **Online First**: Prioritizes downloading the latest Chrome installer from the internet. Falls back to USB if offline.
    *   **Visual C++ Runtimes**: Automatically downloads and installs the latest VC++ 2015-2022 Redistributable (**x64 and x86**).
*   **🔄 Transparent Auto-Updates**:
    *   **Daily Updates**: Registers a hidden scheduled task to run `winget upgrade --all` daily (includes `source update`).
    *   **Silent**: Updates happen in the background without user intervention.

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
*   **Nvidia**: Requires local installer in `drivers/nvidia` or manual URL configuration in script (Auto-download API is deprecated).
*   **Visual C++**: Automatically downloads from Microsoft.

## 📝 Usage

1.  **Prepare USB**: Place `autounattend.xml` in the root of your Windows Installation Media.
2.  **Add Drivers/Apps**: Create the `drivers` folder structure and copy your installers (optional, but recommended for speed).
3.  **Boot**: Boot from the USB.
4.  **Relax**: The system will install Windows, drivers, and apps, and clean itself up automatically. When you see the desktop, it's ready.

## 🛠️ Troubleshooting

*   **Logs**: The full installation log is saved at `C:\Windows\Panther\Autounattend_Log.txt`. Check this file if something didn't install correctly.

---
---

# 🇫🇷 Ultimate Windows Autounattend (Français)

Ce dépôt contient un fichier `autounattend.xml` hautement optimisé et modulaire, conçu pour une installation Windows **silencieuse**, **propre** et **robuste**.

**La fonctionnalité clé :** Toutes les installations de logiciels et de pilotes se font **totalement silencieusement avant la première connexion utilisateur**, garantissant un environnement impeccable dès l'apparition du bureau.

## ✨ Fonctionnalités

*   **⚡ Installation Zéro-Interruption**: Tous les logiciels (Chrome, Pilotes, etc.) sont installés durant la phase `Specialize`, **avant** la connexion de l'utilisateur. Aucun popup, aucune attente sur le bureau.
*   **🤫 Totalement Silencieux**: Tous les scripts sont optimisés pour masquer les sorties et fenêtres. Vous ne verrez rien avant l'écran "Bienvenue".
*   **🛡️ Confidentialité Renforcée**: Désactive la télémétrie, Copilot, la recherche Bing, Cortana, l'ID publicitaire. **Restaure le menu contextuel classique** (Windows 11) et affiche les extensions de fichiers.
*   **🌑 Mode Sombre**: Active le mode sombre pour le système et les applications par défaut.
*   **🧹 Nettoyage en Profondeur**: Supprime agressivement les bloatwares (Candy Crush, Clipchamp, Lien avec téléphone, etc.) et les fonctionnalités Windows inutiles.
*   **💥 Auto-destruction**: Les scripts d'installation se suppriment automatiquement après la première connexion pour garantir un état propre.
*   **📜 Journaux**: Les journaux d'installation sont conservés dans `C:\Windows\Panther\Autounattend_Log.txt` pour le dépannage.
*   **🚀 Optimisation Système**:
    *   **Haute Performance**: Active automatiquement le plan d'alimentation "Haute Performance".
    *   **Utilisateur Avancé**: Active "Fin de tâche" dans le menu contextuel de la barre des tâches.
    *   **Gain d'Espace**: Désactive l'hibernation pour économiser de l'espace disque (`hiberfil.sys`).
    *   **Jeu**: Désactive Game DVR/Bar pour de meilleures performances en jeu.
    *   **IO**: Désactive la mise à jour de l'horodatage "Dernier accès" pour de meilleures performances du système de fichiers.
*   **🔧 Installation Intelligente des Pilotes**:
    *   **Auto-Détection**: Scanne tous les lecteurs pour trouver le dossier `drivers`.
    *   **Recherche Intelligente**: Trouve automatiquement les exécutables (`*.exe`)—pas besoin de renommer en `setup.exe`.
    *   **Support Inclus**: Scripts pour Réseau, GPU Nvidia, Chipset AMD et Audio Focusrite.
*   **🌐 Installation d'Applications Robuste**:
    *   **Connectivité Intelligente**: Vérifie la connexion internet via plusieurs hôtes fiables (Google, Cloudflare, Microsoft).
    *   **En Ligne en Priorité**: Privilégie le téléchargement du dernier installateur Chrome depuis Internet. Bascule sur l'USB si hors ligne.
    *   **Runtimes Visual C++**: Télécharge et installe automatiquement les derniers Runtimes VC++ 2015-2022 (**x64 et x86**).
*   **🔄 Mises à Jour Automatiques Transparentes**:
    *   **Quotidien**: Enregistre une tâche planifiée masquée pour exécuter `winget upgrade --all` chaque jour.
    *   **Silencieux**: Les mises à jour se font en arrière-plan sans intervention de l'utilisateur.

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
*   **Nvidia**: Nécessite un installateur local ou une configuration manuelle de l'URL (L'API d'auto-téléchargement est obsolète).
*   **Visual C++**: Télécharge automatiquement depuis Microsoft.

## 📝 Utilisation

1.  **Préparer la clé USB**: Placez `autounattend.xml` à la racine de votre média d'installation Windows.
2.  **Ajouter Pilotes/Apps**: Créez la structure de dossiers `drivers` et copiez vos installateurs (optionnel, mais recommandé pour la vitesse).
3.  **Démarrer**: Démarrez sur la clé USB.
4.  **Détendez-vous**: Le système installera Windows, les pilotes et les applications, et se nettoiera automatiquement. Quand vous voyez le bureau, c'est prêt.

## 🛠️ Dépannage

*   **Journaux (Logs)**: Le journal d'installation complet est enregistré sous `C:\Windows\Panther\Autounattend_Log.txt`. Consultez ce fichier si quelque chose ne s'est pas installé correctement.
