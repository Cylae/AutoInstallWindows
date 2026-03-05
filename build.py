import re
import html
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def xml_encode(s: str) -> str:
    """Helper function to XML encode content safely."""
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

    # --- Script Updates (Full Sync) ---
    logging.info("Synchronizing scripts directory to autounattend.xml...")

    # Generate the new <File> blocks
    new_file_blocks = []

    # Recursively find all .ps1 files
    for script_file in scripts_dir.rglob('*.ps1'):
        # e.g. scripts/Lib/Helper.ps1 -> Lib/Helper.ps1
        rel_path = script_file.relative_to(scripts_dir)
        # e.g. Lib\Helper.ps1
        win_rel_path = str(rel_path).replace('/', '\\')

        script_full_path = script_file
        with script_full_path.open('r', encoding='utf-8') as f:
            script_content = f.read()

        encoded_content = xml_encode(script_content).strip()
        target_path_str = f"C:\\Windows\\Setup\\Scripts\\{win_rel_path}"

        block = f'\t\t<File path="{target_path_str}">\n{encoded_content}\n</File>'
        new_file_blocks.append(block)
        logging.info(f"Adding/Updating {target_path_str}...")

    # Join all new blocks
    new_files_xml = '\n'.join(new_file_blocks)

    # We replace everything between <Extensions ...> ... </Extensions>
    # EXCEPT for the <ExtractScript> block which must be preserved.
    # Pattern to capture everything inside <Extensions>
    extensions_pattern = r'(<Extensions[^>]*>)(.*?)(</Extensions>)'

    def replace_extensions(match):
        ext_open = match.group(1)
        inner_content = match.group(2)
        ext_close = match.group(3)

        # Extract the <ExtractScript> block to preserve it
        extract_script_pattern = r'(<ExtractScript>.*?</ExtractScript>)'
        extract_match = re.search(extract_script_pattern, inner_content, re.DOTALL)

        if extract_match:
            extract_script_block = extract_match.group(1)
        else:
            extract_script_block = "" # Shouldn't happen in our template

        # Reconstruct the inner content with ExtractScript + New File blocks
        new_inner = f"\n\t\t{extract_script_block}\n{new_files_xml}\n\t"
        return f"{ext_open}{new_inner}{ext_close}"

    content = re.sub(extensions_pattern, replace_extensions, content, flags=re.DOTALL)

    # --- Strip Empty Settings Passes ---
    logging.info("Stripping empty settings passes...")
    empty_pass_pattern = r'\s*<settings pass="[^"]+">\s*</settings>'
    content = re.sub(empty_pass_pattern, '', content)

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
            logging.error("<settings pass=\"specialize\"> not found in autounattend.xml. Cannot inject WiFi.")

    with xml_path.open('w', encoding='utf-8') as f:
        f.write(content)

    logging.info("autounattend.xml updated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build and update autounattend.xml with scripts and optional WiFi settings.")
    parser.add_argument('--wifi-ssid', help='SSID for the WiFi network')
    parser.add_argument('--wifi-pass', help='Password for the WiFi network')

    args = parser.parse_args()
    update_autounattend(ssid=args.wifi_ssid, password=args.wifi_pass)
