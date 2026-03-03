import re
import argparse
import html
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def remove_empty_passes(content: str) -> str:
    """Removes empty settings passes from the XML content."""
    passes_to_check = ['offlineServicing', 'generalize', 'auditSystem', 'auditUser']
    for p in passes_to_check:
        # Match exactly <settings pass="name"></settings> with optional whitespace
        pattern = r'<settings pass="' + p + r'">\s*</settings>\n?'
        content = re.sub(pattern, '', content)
    return content

def update_autounattend(ssid: str = None, password: str = None):
    xml_path = Path('autounattend.xml')
    scripts_dir = Path('scripts')

    if not xml_path.exists():
        logging.error(f"{xml_path} not found.")
        return

    content = xml_path.read_text(encoding='utf-8')

    # --- Script Synchronization ---
    # First, remove all existing <File path="C:\Windows\Setup\Scripts\..."> blocks
    # to ensure a clean synchronization with the file system.
    file_block_pattern = r'(<File path="C:\\Windows\\Setup\\Scripts\\[^"]+">.*?</File>\n?)'
    content = re.sub(file_block_pattern, '', content, flags=re.DOTALL)

    # Now, find the <ExtractScript> block to append our new <File> blocks right after it
    extract_script_pattern = r'(<ExtractScript>.*?</ExtractScript>\n)'
    match = re.search(extract_script_pattern, content, re.DOTALL)
    if not match:
        logging.error("Could not find <ExtractScript> block in autounattend.xml. Cannot sync scripts.")
        return

    insertion_point = match.end()

    # Collect all script contents to insert
    new_file_blocks = ""
    for file_path in sorted(scripts_dir.rglob('*.ps1')):
        # Construct the relative path from scripts_dir
        rel_path = file_path.relative_to(scripts_dir)
        win_rel_path = str(rel_path).replace('/', '\\')

        target_path_str = f"C:\\Windows\\Setup\\Scripts\\{win_rel_path}"

        script_content = file_path.read_text(encoding='utf-8')
        encoded_content = html.escape(script_content, quote=True)

        logging.info(f"Adding {target_path_str}...")
        new_file_blocks += f'\t\t<File path="{target_path_str}">\n{encoded_content}\n</File>\n'

    # Insert the new file blocks
    content = content[:insertion_point] + new_file_blocks + content[insertion_point:]


    # --- WiFi Injection ---
    if ssid and password:
        logging.info(f"Injecting WiFi Profile for SSID: {ssid}")

        # XML Encode SSID and Password
        safe_ssid = html.escape(ssid, quote=True)
        safe_password = html.escape(password, quote=True)

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

        specialize_pattern = r'(<settings pass="specialize">)(.*?)(</settings>)'
        match_specialize = re.search(specialize_pattern, content, re.DOTALL)

        if match_specialize:
            specialize_content = match_specialize.group(2)

            wlan_comp_pattern = r'(<component name="Microsoft-Windows-Wlan-Svc".*?>)(.*?)(</component>)'
            match_wlan = re.search(wlan_comp_pattern, specialize_content, re.DOTALL)

            if match_wlan:
                logging.info("Updating existing Microsoft-Windows-Wlan-Svc component...")
                new_wlan_comp = match_wlan.group(1) + wlan_profile + "\n" + match_wlan.group(3)
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

    # --- Remove Empty Passes ---
    content = remove_empty_passes(content)

    xml_path.write_text(content, encoding='utf-8')
    logging.info("autounattend.xml updated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build and update autounattend.xml with scripts and optional WiFi settings.")
    parser.add_argument('--wifi-ssid', help='SSID for the WiFi network')
    parser.add_argument('--wifi-pass', help='Password for the WiFi network')

    args = parser.parse_args()

    update_autounattend(ssid=args.wifi_ssid, password=args.wifi_pass)
