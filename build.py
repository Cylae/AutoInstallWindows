import re
import os
import html
import argparse
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Helper function to XML encode content
def xml_encode(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    return s

def update_autounattend(ssid=None, password=None):
    xml_path = Path('autounattend.xml')
    scripts_dir = Path('scripts')

    if not xml_path.exists():
        logging.error(f"{xml_path} not found.")
        return

    with xml_path.open('r', encoding='utf-8') as f:
        content = f.read()

    # --- Script Synchronization ---
    local_scripts = {}
    for script_file in scripts_dir.rglob('*.ps1'):
        rel_path = script_file.relative_to(scripts_dir)
        win_rel_path = str(rel_path).replace(os.sep, '\\')
        target_path_str = f"C:\\Windows\\Setup\\Scripts\\{win_rel_path}"

        with script_file.open('r', encoding='utf-8') as f:
            script_content = f.read()
        local_scripts[target_path_str] = xml_encode(script_content).strip()

    existing_paths = set()
    for match in re.finditer(r'<File path="([^"]+)">', content):
        existing_paths.add(match.group(1))

    def sync_file_block(match):
        indent = match.group(1)
        path = match.group(2)
        if path.startswith("C:\\Windows\\Setup\\Scripts\\"):
            if path in local_scripts:
                logging.info(f"Updating {path}...")
                return f'{indent}<File path="{path}">\n{local_scripts[path]}\n{indent}</File>\n'
            else:
                logging.info(f"Removing {path} (not found in local scripts)...")
                return ""
        else:
            return match.group(0)

    pattern = r'([ \t]*)<File path="([^"]+)">(.*?)</File>\n?'
    content = re.sub(pattern, sync_file_block, content, flags=re.DOTALL)

    new_blocks = []
    for path, script_content in local_scripts.items():
        if path not in existing_paths:
            logging.info(f"Adding new script {path}...")
            new_blocks.append(f'\t\t<File path="{path}">\n{script_content}\n\t\t</File>\n')

    if new_blocks:
        new_blocks_str = "".join(new_blocks)
        content = re.sub(r'([ \t]*)(</Extensions>)', lambda m: new_blocks_str + m.group(1) + m.group(2), content)

    # --- XML Cleanup (Empty Passes) ---
    empty_passes = ['offlineServicing', 'generalize', 'auditSystem', 'auditUser']
    for p in empty_passes:
        # Match <settings pass="...">\s*</settings> and remove them
        pattern = r'[ \t]*<settings pass="' + p + r'">\s*</settings>\n?'
        if re.search(pattern, content):
            logging.info(f"Removing empty settings pass '{p}'...")
            content = re.sub(pattern, '', content)

    # --- WiFi Injection ---
    if ssid and password:
        logging.info(f"Injecting WiFi Profile for SSID: {ssid}")

        safe_ssid = xml_encode(ssid)
        safe_password = xml_encode(password)

        wlan_profile = f"""
            <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
                <name>{safe_ssid}</name>
                <SSIDConfig>
                    <SSID>
                        <name>{safe_ssid}</name>
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
                            <keyMaterial>{safe_password}</keyMaterial>
                        </sharedKey>
                    </security>
                </MSM>
            </WLANProfile>
        """

        specialize_pattern = r'(<settings pass="specialize">)(.*?)(</settings>)'
        match_specialize = re.search(specialize_pattern, content, re.DOTALL)

        if match_specialize:
            specialize_content = match_specialize.group(2)
            wlan_comp_pattern = r'(<component name="Microsoft-Windows-Wlan-Svc".*?>)(.*?)(</component>)'
            match_wlan = re.search(wlan_comp_pattern, specialize_content, re.DOTALL)

            if match_wlan:
                logging.info("Updating existing Microsoft-Windows-Wlan-Svc component...")
                new_wlan_comp = match_wlan.group(1) + wlan_profile + match_wlan.group(3)
                new_specialize_content = re.sub(wlan_comp_pattern, lambda m: new_wlan_comp, specialize_content, flags=re.DOTALL)
            else:
                logging.info("Adding Microsoft-Windows-Wlan-Svc component...")
                wlan_component = f"""
            <component name="Microsoft-Windows-Wlan-Svc" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                {wlan_profile}
            </component>
                """
                new_specialize_content = specialize_content + wlan_component

            full_replacement = match_specialize.group(1) + new_specialize_content + match_specialize.group(3)
            content = content.replace(match_specialize.group(0), full_replacement)
        else:
            logging.error('<settings pass="specialize"> not found in autounattend.xml. Cannot inject WiFi.')

    with xml_path.open('w', encoding='utf-8') as f:
        f.write(content)

    logging.info("autounattend.xml updated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build and update autounattend.xml with scripts and optional WiFi settings.")
    parser.add_argument('--wifi-ssid', help='SSID for the WiFi network')
    parser.add_argument('--wifi-pass', help='Password for the WiFi network')

    args = parser.parse_args()
    update_autounattend(ssid=args.wifi_ssid, password=args.wifi_pass)
