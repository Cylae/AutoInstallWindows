import re
import argparse
import logging
from pathlib import Path

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

    with open(xml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # --- Script Updates (Full Sync) ---
    extensions_pattern = r'(<Extensions xmlns="https://schneegans\.de/windows/unattend-generator/">)(.*?)(</Extensions>)'
    match_extensions = re.search(extensions_pattern, content, re.DOTALL)

    if match_extensions:
        extensions_content = match_extensions.group(2)

        # 1. Extract existing <File> blocks
        file_block_pattern = r'(<File path="([^"]+)">)(.*?)(</File>)'
        existing_files = {}
        for match in re.finditer(file_block_pattern, extensions_content, re.DOTALL):
            existing_files[match.group(2)] = match.group(0)

        # 2. Build new <File> blocks based on actual scripts/ directory
        new_file_blocks = {}
        expected_paths = set()
        for script_file in scripts_dir.rglob('*.ps1'):
            rel_path = script_file.relative_to(scripts_dir)
            win_rel_path = str(rel_path).replace('/', '\\')

            with open(script_file, 'r', encoding='utf-8') as f:
                script_content = f.read()

            encoded_content = xml_encode(script_content)
            target_path_str = f"C:\\Windows\\Setup\\Scripts\\{win_rel_path}"
            expected_paths.add(target_path_str)

            new_file_blocks[target_path_str] = f'<File path="{target_path_str}">\n{encoded_content.strip()}\n</File>'

        # 3. Synchronize
        updated_extensions_content = extensions_content

        # Remove deleted files
        for old_path, old_block in existing_files.items():
            if old_path not in expected_paths and old_path.startswith("C:\\Windows\\Setup\\Scripts\\"):
                logging.info(f"Removing deleted script from XML: {old_path}")
                updated_extensions_content = updated_extensions_content.replace(old_block, "")

        # Update or Add files
        for new_path, new_block in new_file_blocks.items():
            if new_path in existing_files:
                if existing_files[new_path] != new_block:
                    logging.info(f"Updating script in XML: {new_path}")
                    updated_extensions_content = updated_extensions_content.replace(existing_files[new_path], new_block)
            else:
                logging.info(f"Adding new script to XML: {new_path}")
                updated_extensions_content = updated_extensions_content.strip() + f"\n\t\t{new_block}\n"

        # Apply synchronized extensions back to main content
        new_extensions_block = match_extensions.group(1) + updated_extensions_content + match_extensions.group(3)
        content = content.replace(match_extensions.group(0), new_extensions_block)
    else:
        logging.error("<Extensions> block not found in autounattend.xml.")

    # --- WiFi Injection ---
    if ssid and password:
        logging.info(f"Injecting WiFi Profile for SSID: {ssid}")

        # XML Encode SSID and Password
        safe_ssid = xml_encode(ssid)
        safe_password = xml_encode(password)

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
            logging.error("<settings pass=\"specialize\"> not found in autounattend.xml. Cannot inject WiFi.")

    # --- Clean up empty passes ---
    empty_passes = ['offlineServicing', 'generalize', 'auditSystem', 'auditUser']
    for p in empty_passes:
        # Pattern to match <settings pass="p"></settings> possibly with whitespace
        empty_pattern = r'[ \t]*<settings pass="' + p + r'">\s*</settings>\n?'
        if re.search(empty_pattern, content):
            logging.info(f"Removing empty settings pass: {p}")
            content = re.sub(empty_pattern, '', content)

    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(content)

    logging.info("autounattend.xml updated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build and update autounattend.xml with scripts and optional WiFi settings.")
    parser.add_argument('--wifi-ssid', help='SSID for the WiFi network')
    parser.add_argument('--wifi-pass', help='Password for the WiFi network')

    args = parser.parse_args()

    update_autounattend(ssid=args.wifi_ssid, password=args.wifi_pass)
