import re
import argparse
import logging
from pathlib import Path
import html

# Setup structured logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def update_autounattend(ssid=None, password=None):
    xml_path = Path('autounattend.xml')
    scripts_dir = Path('scripts')

    if not xml_path.exists():
        logging.error(f"{xml_path} not found.")
        return

    content = xml_path.read_text(encoding='utf-8')

    # --- Script Updates ---

    # 1. Gather all local .ps1 files from scripts/ directory
    local_scripts = {}
    for script_file in scripts_dir.rglob('*.ps1'):
        # e.g. scripts/Lib/Helper.ps1 -> Lib\Helper.ps1
        rel_path = script_file.relative_to(scripts_dir)
        win_rel_path = str(rel_path).replace('/', '\\')
        target_path_str = rf"C:\Windows\Setup\Scripts\{win_rel_path}"

        script_content = script_file.read_text(encoding='utf-8')
        encoded_content = html.escape(script_content)

        local_scripts[target_path_str] = encoded_content

    # 2. Extract existing <File> tags inside <Extensions>
    extensions_pattern = r'(<Extensions.*?>)(.*?)(</Extensions>)'
    extensions_match = re.search(extensions_pattern, content, re.DOTALL)

    if not extensions_match:
        logging.error("Could not find <Extensions> block in autounattend.xml.")
        return

    extensions_start = extensions_match.group(1)
    extensions_content = extensions_match.group(2)
    extensions_end = extensions_match.group(3)

    # 3. Synchronize files (Update existing, remove missing, add new)
    file_pattern = r'<File path="(.*?)">(.*?)</File>'
    existing_files_in_xml = {}

    # Track files to keep
    def replacement_func(match):
        xml_file_path = match.group(1)

        if xml_file_path in local_scripts:
            # Update content
            logging.info(f"Updating {xml_file_path}...")
            existing_files_in_xml[xml_file_path] = True
            return f'<File path="{xml_file_path}">\n{local_scripts[xml_file_path].strip()}\n</File>'
        elif xml_file_path.startswith("C:\\Windows\\Setup\\Scripts\\"):
            # Remove from XML if it's no longer in the file system
             logging.info(f"Removing {xml_file_path} from XML (file not found).")
             return ''
        else:
             # Keep other files not managed by our scripts folder
             return match.group(0)

    updated_extensions_content = re.sub(file_pattern, replacement_func, extensions_content, flags=re.DOTALL)

    # Add missing files
    for local_file_path, local_content in local_scripts.items():
        if local_file_path not in existing_files_in_xml:
            logging.info(f"Adding new file {local_file_path} to XML...")
            new_file_block = f'\n\t\t<File path="{local_file_path}">\n{local_content.strip()}\n</File>'
            updated_extensions_content += new_file_block

    # Put it all back together
    new_extensions_block = f"{extensions_start}{updated_extensions_content}{extensions_end}"
    content = content.replace(extensions_match.group(0), new_extensions_block)

    # --- Clean up empty settings passes ---
    # Find passes like <settings pass="offlineServicing"></settings> or with whitespace
    empty_pass_pattern = r'<settings pass="(offlineServicing|generalize|auditSystem|auditUser)">\s*</settings>\n*'
    content = re.sub(empty_pass_pattern, '', content)

    # --- WiFi Injection ---
    if ssid and password:
        logging.info(f"Injecting WiFi Profile for SSID: {ssid}")

        # XML Encode SSID and Password
        safe_ssid = html.escape(ssid)
        safe_password = html.escape(password)

        # XML Block for WLAN Profile
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

        # We need to inject this into the "specialize" pass.
        # Check if Microsoft-Windows-Wlan-Svc component already exists in specialize pass.
        # Regex to find the specialize pass and the component within it.

        # Strategy:
        # 1. Find <settings pass="specialize">
        # 2. Check if <component name="Microsoft-Windows-Wlan-Svc" ...> exists inside it.
        # 3. If yes, replace its content (or append). If no, insert it.

        specialize_pattern = r'(<settings pass="specialize">)(.*?)(</settings>)'
        match_specialize = re.search(specialize_pattern, content, re.DOTALL)

        if match_specialize:
            specialize_content = match_specialize.group(2)

            wlan_comp_pattern = r'(<component name="Microsoft-Windows-Wlan-Svc".*?>)(.*?)(</component>)'
            match_wlan = re.search(wlan_comp_pattern, specialize_content, re.DOTALL)

            if match_wlan:
                # Component exists, replace its content with our profile
                logging.info("Updating existing Microsoft-Windows-Wlan-Svc component...")
                new_wlan_comp = match_wlan.group(1) + wlan_profile + match_wlan.group(3)
                new_specialize_content = re.sub(wlan_comp_pattern, lambda m: new_wlan_comp, specialize_content, flags=re.DOTALL)
            else:
                # Component does not exist, append it to the end of specialize settings
                logging.info("Adding Microsoft-Windows-Wlan-Svc component...")
                # We need the full component definition including attributes
                wlan_component = f"""
            <component name="Microsoft-Windows-Wlan-Svc" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                {wlan_profile}
            </component>
                """
                new_specialize_content = specialize_content + wlan_component

            # Replace the old specialize content with the new one
            # We must be careful to replace only the content inside the tags

            # A safer way to replace the whole block in the main content:
            full_replacement = match_specialize.group(1) + new_specialize_content + match_specialize.group(3)
            content = content.replace(match_specialize.group(0), full_replacement)

        else:
            logging.error('Error: <settings pass="specialize"> not found in autounattend.xml. Cannot inject WiFi.')

    xml_path.write_text(content, encoding='utf-8')

    logging.info("autounattend.xml updated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build and update autounattend.xml with scripts and optional WiFi settings.")
    parser.add_argument('--wifi-ssid', help='SSID for the WiFi network')
    parser.add_argument('--wifi-pass', help='Password for the WiFi network')

    args = parser.parse_args()

    update_autounattend(ssid=args.wifi_ssid, password=args.wifi_pass)
