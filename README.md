# 🚀 Ultimate Windows Autounattend

**New! Easy Personalization GUI:** We now include a user-friendly graphical tool (`personalize.py`) so you can easily adapt the `autounattend.xml` to your needs before copying it to your USB. Just run `python personalize.py` to open the GUI and configure your Username, Password, Time Zone, Computer Name, Language, and WiFi!

This repository contains a highly optimized, modular `autounattend.xml` designed for a **silent**, **clean**, and **robust** Windows installation.

**The defining feature:** All software and driver installations occur **completely silently before the first user login**, ensuring a pristine environment the moment the desktop appears.

## ✨ Features

*   **⚡ Zero-Interruption Setup**: All software (Chrome, Drivers, etc.) is installed during the `Specialize` pass, *before* the user logs in. No popups, no waiting at the desktop.
*   **🤫 Totally Silent**: All scripts are optimized to suppress output and windows. You won't see a thing until the "Welcome" screen.
*   **🛡️ Privacy Hardened**: Disables Telemetry, **Recall** (AI Screenshot), Copilot, Bing Search, Cortana, Advertising ID, **Search Highlights**, **Widgets**, **File Explorer Ads**, **Tips/Suggestions**, **Error Reporting**, **Shared Experiences**, **Location Tracking**, **Delivery Optimization**, and **Typing Insights**. **Restores Classic Context Menu** (Windows 11) and shows file extensions by default.
*   **🌑 Dark Mode**: Enables Dark Mode for System and Apps by default.
*   **🧹 Deep Debloating**: Aggressively removes bloatware (Candy Crush, Clipchamp, **Widgets**, **Cortana**, **Xbox/Gaming Overlays**, **YourPhone**, **Meet Now** icon, etc.) and unnecessary Windows capabilities. **Preserves Notepad and Paint.**
*   **💥 Self-Destruct**: Installation scripts automatically delete themselves after the first login to ensure a clean slate.
*   **📜 Log Persistence**: Setup logs are preserved in `C:\Windows\Panther\Autounattend_Log.txt` for troubleshooting.
*   **🚀 System Optimization**:
    *   **High Performance**: Automatically sets the "High Performance" power plan.
    *   **Power User**: Enables "End Task" in Taskbar context menu, shows **Seconds in System Clock**, and Disables Transparency effects.
    *   **User Experience**: Disables "Finish setting up your device", "Lock Screen Tips", "Welcome Experience", "Sync Provider Notifications", **Widgets (News and Interests)**, **Chat/Teams** icon, **Mouse Acceleration** (Enhance Pointer Precision), and prevents accidental **Accessibility Shortcuts** (Sticky Keys).
    *   **Space Saving**: Disables Hibernation to save disk space (`hiberfil.sys`).
    *   **Performance**: Disables Last Access Timestamp updates and **App Launch Tracking** to improve disk performance.
    *   **Gaming**: Disables Game DVR/Bar for better gaming performance.
*   **🔧 Intelligent Driver Installation**:
    *   **Auto-Detection**: Automatically scans all drives for a `drivers` folder.
    *   **Smart Matching**: Finds installer executables (`*.exe`) automatically—no need to rename files to `setup.exe`.
    *   **Included Support**: Scripts for Network, Nvidia GPU, AMD Chipset, and Focusrite Audio drivers.
*   **🌐 Robust App Installation**:
    *   **Smart Connectivity**: Verified internet checks against multiple reliable hosts (Google, Cloudflare, Microsoft) with robust retry logic.
    *   **Online First**: Prioritizes downloading the latest Chrome and Visual C++ Runtimes from the internet.
    *   **Offline Fallback**: Automatically checks for local installers if internet is unavailable.
    *   **Visual C++ Runtimes**: Automatically downloads and installs the latest VC++ 2015-2022 Redistributable (**x64 and x86**).
*   **🔄 Transparent Auto-Updates**:
    *   **Daily Updates**: Registers a hidden scheduled task to run `winget upgrade --all` daily (includes `source update`).
    *   **Silent**: Updates happen in the background without user intervention (configured with `--disable-interactivity`).
*   **🛡️ Enhanced Robustness**:
    *   **Secure Downloads**: Supports **TLS 1.2 and 1.3** for secure file downloads.
    *   **Smart Media Detection**: Filters for Fixed and Removable drives to prevent hangs on network/floppy drives.
    *   **Fail-Safe Execution**: Scripts include existence checks (e.g., RunOnce) to prevent errors on subsequent logins.
    *   **Advanced Error Handling**: Improved logging and registry handling for fail-safe execution.

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
        ├── chrome/        (Place Chrome Installer .exe here)
        ├── vcredist_x64/  (Place VC++ x64 Installer .exe here)
        └── vcredist_x86/  (Place VC++ x86 Installer .exe here)
```

### 🌍 Internet Download

*   **Chrome**: Preferentially downloads and installs the **Enterprise MSI** for optimal silent deployment. Supports both `.msi` and `.exe` local installers.
*   **Visual C++**: Automatically downloads from Microsoft, falls back to local `vcredist_x64`/`vcredist_x86` folders if offline.
*   **Nvidia**: Requires local installer in `drivers/nvidia` or manual URL configuration in script.

## 📝 Usage

1.  **Prepare USB**: Place `autounattend.xml` in the root of your Windows Installation Media.
2.  **Add Drivers/Apps**: Create the `drivers` folder structure and copy your installers (optional, but recommended for speed).
3.  **Boot**: Boot from the USB.
4.  **Relax**: The system will install Windows, drivers, and apps, and clean itself up automatically. When you see the desktop, it's ready.


5. **Personalize (Optional but Recommended)**: Before copying `autounattend.xml` to your USB drive, you can run the interactive personalization tool to easily set your Username, Password, Language, Computer Name, TimeZone, and WiFi credentials. *If you run this on your current Windows machine, it will automatically detect and suggest your current settings!*
   ```bash
   python personalize.py
   ```

## 🛠️ For Developers

This repository uses a build system to generate `autounattend.xml` from modular PowerShell scripts. `build.py` automatically injects scripts, creates `<File>` blocks if they are missing, and removes empty XML blocks for a cleaner file.

*   **Scripts Location**: All PowerShell scripts are located in the `scripts/` directory.
*   **Modify**: Edit the `.ps1` files in `scripts/` to make changes.
*   **Build**: Run `python build.py` to regenerate `autounattend.xml` with your changes. (Now uses `pathlib` and `logging` for robust builds).
*   **Test**: Run `pytest` to execute unit tests.
*   **Lint**: Run `flake8` to lint Python files.

## ❓ Troubleshooting

If you encounter issues, check the log file created during setup:
**`C:\Windows\Panther\Autounattend_Log.txt`**

*   **Drivers not installing?**
    *   Ensure network drivers are **`.inf`** files (extract them if necessary) placed in `drivers/network`.
    *   Ensure other drivers (Nvidia, AMD, etc.) are **`.exe`** installers.
    *   Verify the folder structure on your USB drive matches the example above.
*   **Apps not downloading?**
    *   Check your internet connection. The script attempts to connect to `google.com` to verify connectivity.
    *   If offline, place the installers in the corresponding `apps` folder on the USB.
*   **Script errors?**
    *   Review the log file mentioned above for specific error messages (now with millisecond precision!).
    *   Additional debug logs for drivers (e.g., `pnputil`) are saved in `%TEMP%` during setup.

## 📡 WiFi Configuration

For a **Zero-Interruption** experience, a wired Ethernet connection is strongly recommended.

### Easy Method (Recommended)

You can automatically inject your WiFi credentials into `autounattend.xml` using the build script:

```bash
python build.py --wifi-ssid "MyNetwork" --wifi-pass "MyPassword"
```

### Manual Method

If you prefer to edit the XML manually, add your network profile inside the `<specialize>` pass. Add the following XML block (customized with your details) inside the `<component name="Microsoft-Windows-Wlan-Svc">`:

```xml
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>YourSSID</name>
    <SSIDConfig>
        <SSID>
            <name>YourSSID</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>YourPassword</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>
```

---
---

# 🇫🇷 Ultimate Windows Autounattend (Français)

**Nouveau ! Interface de Personnalisation Facile :** Nous incluons désormais un outil graphique convivial (`personalize.py`) pour vous permettre d'adapter facilement le fichier `autounattend.xml` à vos besoins avant de le copier sur votre clé USB. Exécutez simplement `python personalize.py` pour ouvrir l'interface et configurer votre Nom d'utilisateur, Mot de passe, Fuseau horaire, Nom de l'ordinateur, Langue et WiFi !

Ce dépôt contient un fichier `autounattend.xml` hautement optimisé et modulaire, conçu pour une installation Windows **silencieuse**, **propre** et **robuste**.

**La fonctionnalité clé :** Toutes les installations de logiciels et de pilotes se font **totalement silencieusement avant la première connexion utilisateur**, garantissant un environnement impeccable dès l'apparition du bureau.

## ✨ Fonctionnalités

*   **⚡ Installation Zéro-Interruption**: Tous les logiciels (Chrome, Pilotes, etc.) sont installés durant la phase `Specialize`, **avant** la connexion de l'utilisateur. Aucun popup, aucune attente sur le bureau.
*   **🤫 Totalement Silencieux**: Tous les scripts sont optimisés pour masquer les sorties et fenêtres. Vous ne verrez rien avant l'écran "Bienvenue".
*   **🛡️ Confidentialité Renforcée**: Désactive la télémétrie, **Recall** (Capture d'écran IA), Copilot, la recherche Bing, Cortana, l'ID publicitaire, **Widgets**, **Publicités Explorateur**, **Astuces**, **Rapports d'erreurs**, **Expériences partagées**, **Suivi de localisation**, **Optimisation de la distribution** et **Insights de saisie**. **Restaure le menu contextuel classique** (Windows 11) et affiche les extensions de fichiers.
*   **🌑 Mode Sombre**: Active le mode sombre pour le système et les applications par défaut.
*   **🧹 Nettoyage en Profondeur**: Supprime agressivement les bloatwares (Candy Crush, Clipchamp, **Widgets**, **Cortana**, **Xbox/Jeux**, **YourPhone**, **Meet Now**, etc.) et les fonctionnalités Windows inutiles. **Préserve Notepad et Paint.**
*   **💥 Auto-destruction**: Les scripts d'installation se suppriment automatiquement après la première connexion pour garantir un état propre.
*   **📜 Journaux**: Les journaux d'installation sont conservés dans `C:\Windows\Panther\Autounattend_Log.txt` pour le dépannage.
*   **🚀 Optimisation Système**:
    *   **Haute Performance**: Active automatiquement le plan d'alimentation "Haute Performance".
    *   **Utilisateur Avancé**: Active "Fin de tâche" dans le menu contextuel, affiche les **Secondes dans l'horloge**, et désactive la transparence.
    *   **Expérience Utilisateur**: Désactive "Terminer la configuration de votre appareil", les astuces de l'écran de verrouillage, l'expérience de bienvenue, **Widgets (Actualités)**, l'icône **Chat/Teams**, l'**Accélération de la souris** (Améliorer la précision du pointeur) et empêche l'activation accidentelle des **Raccourcis d'accessibilité** (Touches rémanentes).
    *   **Gain d'Espace**: Désactive l'hibernation pour économiser de l'espace disque (`hiberfil.sys`).
    *   **Performance**: Désactive la mise à jour de la date de dernier accès et le **Suivi de lancement d'applications** pour améliorer les performances disque.
    *   **Jeu**: Désactive Game DVR/Bar pour de meilleures performances en jeu.
*   **🔧 Installation Intelligente des Pilotes**:
    *   **Auto-Détection**: Scanne tous les lecteurs pour trouver le dossier `drivers`.
    *   **Recherche Intelligente**: Trouve automatiquement les exécutables (`*.exe`)—pas besoin de renommer en `setup.exe`.
    *   **Support Inclus**: Scripts pour Réseau, GPU Nvidia, Chipset AMD et Audio Focusrite.
*   **🌐 Installation d'Applications Robuste**:
    *   **Connectivité Intelligente**: Vérifie la connexion internet via plusieurs hôtes fiables (Google, Cloudflare, Microsoft).
    *   **En Ligne en Priorité**: Privilégie le téléchargement du dernier installateur Chrome et Visual C++ depuis Internet.
    *   **Repli Hors-ligne**: Vérifie automatiquement les installateurs locaux si Internet n'est pas disponible.
    *   **Runtimes Visual C++**: Télécharge et installe automatiquement les derniers Runtimes VC++ 2015-2022 (**x64 et x86**).
*   **🔄 Mises à Jour Automatiques Transparentes**:
    *   **Quotidien**: Enregistre une tâche planifiée masquée pour exécuter `winget upgrade --all` chaque jour.
    *   **Silencieux**: Les mises à jour se font en arrière-plan sans intervention de l'utilisateur (configuré avec `--disable-interactivity`).
*   **🛡️ Robustesse Améliorée**:
    *   **Téléchargements Sécurisés**: Supporte **TLS 1.2 et 1.3** pour des téléchargements sécurisés.
    *   **Détection Intelligente**: Filtre les lecteurs Fixes et Amovibles pour éviter les blocages.
    *   **Gestion d'Erreurs Avancée**: Journaux améliorés et gestion robuste du registre pour une exécution sans faille.

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
        ├── chrome/        (Placez l'installateur Chrome .exe ici)
        ├── vcredist_x64/  (Placez l'installateur VC++ x64 .exe ici)
        └── vcredist_x86/  (Placez l'installateur VC++ x86 .exe ici)
```

### 🌍 Téléchargement Internet

*   **Chrome**: Télécharge et installe de préférence le **MSI Entreprise** pour un déploiement silencieux optimal. Supporte les installateurs locaux `.msi` et `.exe`.
*   **Visual C++**: Télécharge automatiquement depuis Microsoft, bascule sur les dossiers `vcredist_x64`/`vcredist_x86` si hors-ligne.
*   **Nvidia**: Nécessite un installateur local ou une configuration manuelle de l'URL.

## 📝 Utilisation

1.  **Préparer la clé USB**: Placez `autounattend.xml` à la racine de votre média d'installation Windows.
2.  **Ajouter Pilotes/Apps**: Créez la structure de dossiers `drivers` et copiez vos installateurs (optionnel, mais recommandé pour la vitesse).
3.  **Démarrer**: Démarrez sur la clé USB.
4.  **Détendez-vous**: Le système installera Windows, les pilotes et les applications, et se nettoiera automatiquement. Quand vous voyez le bureau, c'est prêt.


5. **Personnaliser (Optionnel mais Recommandé)**: Avant de copier `autounattend.xml` sur votre clé USB, vous pouvez exécuter l'outil de personnalisation interactif pour définir facilement votre nom d'utilisateur, mot de passe, langue, nom d'ordinateur, fuseau horaire et identifiants WiFi. *Si vous l'exécutez sur votre machine Windows actuelle, il détectera et suggérera automatiquement vos paramètres actuels !*
   ```bash
   python personalize.py
   ```

## 🛠️ Pour les Développeurs

Ce dépôt utilise un système de build pour générer `autounattend.xml` à partir de scripts PowerShell modulaires. `build.py` injecte automatiquement les scripts, crée des blocs `<File>` s'ils sont manquants et supprime les blocs XML vides pour un fichier plus propre.

*   **Emplacement des Scripts**: Tous les scripts PowerShell se trouvent dans le répertoire `scripts/`.
*   **Modifier**: Éditez les fichiers `.ps1` dans `scripts/` pour apporter des modifications.
*   **Construire**: Exécutez `python build.py` pour régénérer `autounattend.xml` avec vos changements. (Utilise désormais `pathlib` et `logging` pour des builds robustes).
*   **Tester**: Exécutez `pytest` pour lancer les tests unitaires.
*   **Linter**: Exécutez `flake8` pour linter les fichiers Python.

## ❓ Dépannage

Si vous rencontrez des problèmes, consultez le fichier journal créé lors de l'installation :
**`C:\Windows\Panther\Autounattend_Log.txt`**

*   **Les pilotes ne s'installent pas ?**
    *   Assurez-vous que les pilotes réseau sont des fichiers **`.inf`** (extrayez-les si nécessaire) placés dans `drivers/network`.
    *   Assurez-vous que les autres pilotes (Nvidia, AMD, etc.) sont des installateurs **`.exe`**.
    *   Vérifiez que la structure des dossiers sur votre clé USB correspond à l'exemple ci-dessus.
*   **Les applications ne se téléchargent pas ?**
    *   Vérifiez votre connexion Internet. Le script tente de se connecter à `google.com` pour vérifier la connectivité.
    *   Si vous êtes hors ligne, placez les installateurs dans le dossier `apps` correspondant sur la clé USB.
*   **Erreurs de script ?**
    *   Consultez le fichier journal mentionné ci-dessus pour les messages d'erreur spécifiques (maintenant avec une précision à la milliseconde !).
    *   Des journaux de débogage supplémentaires pour les pilotes (ex: `pnputil`) sont enregistrés dans `%TEMP%` pendant l'installation.

## 📡 Configuration WiFi

Pour une expérience **Zéro-Interruption**, une connexion Ethernet filaire est fortement recommandée.

### Méthode Facile (Recommandée)

Vous pouvez injecter automatiquement vos identifiants WiFi dans `autounattend.xml` en utilisant le script de construction :

```bash
python build.py --wifi-ssid "MonReseau" --wifi-pass "MonMotDePasse"
```

### Méthode Manuelle

Si vous préférez éditer le XML manuellement, ajoutez votre profil réseau durant la phase `<specialize>`. Ajoutez le bloc XML suivant (personnalisé avec vos détails) à l'intérieur du composant `<component name="Microsoft-Windows-Wlan-Svc">`:

```xml
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>VotreSSID</name>
    <SSIDConfig>
        <SSID>
            <name>VotreSSID</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>VotreMotDePasse</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>
```
