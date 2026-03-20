import re
import html
import argparse
import logging
from pathlib import Path

# Configure logging
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

    content = xml_path.read_text(encoding='utf-8')

    # --- Script Updates ---
    # Iterate over all files in scripts directory
    for script_full_path in scripts_dir.rglob('*.ps1'):
        # Construct the relative path from scripts_dir
        # e.g. scripts/Lib/Helper.ps1 -> Lib/Helper.ps1
        rel_path = script_full_path.relative_to(scripts_dir)

        # Convert to Windows path style for XML matching
        # e.g. Lib\Helper.ps1
        win_rel_path = str(rel_path).replace('/', '\\')

        # The full path in XML is C:\Windows\Setup\Scripts\<win_rel_path>
        # However, the XML generator often uses forward slashes in attributes or escaped backslashes.
        # We match the specific <File path="C:\Windows\Setup\Scripts\..."> block.

        # Let's read the script content first.
        script_content = script_full_path.read_text(encoding='utf-8')

        # Prepare encoded content
        encoded_content = xml_encode(script_content)

        # Regex to replace content
        # We need to construct the exact path string expected in the XML.
        # Assuming standard path: C:\Windows\Setup\Scripts\SubDir\File.ps1
        target_path_str = f"C:\\Windows\\Setup\\Scripts\\{win_rel_path}"

        # Escape for regex
        escaped_path = re.escape(target_path_str)

        # Pattern: <File path="...target_path_str...">Content</File>
        pattern = r'(<File path="' + escaped_path + r'">)(.*?)(</File>)'

        if re.search(pattern, content, re.DOTALL):
            logging.info(f"Updating {target_path_str}...")
            # Replacement function to preserve the surrounding tags
            def replacement(match):
                return match.group(1) + '\n' + encoded_content.strip() + '\n' + match.group(3)

            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            logging.info(f"File path {target_path_str} not found in XML. Appending it...")
            # Append a new <File> block just before the closing </Extensions> tag.
            new_file_block = f'<File path="{target_path_str}">\n{encoded_content.strip()}\n</File>'
            # Look for </Extensions> and insert the block before it.
            extensions_close_pattern = r'(</Extensions>)'
            if re.search(extensions_close_pattern, content):
                content = re.sub(extensions_close_pattern, f'{new_file_block}\n\t\\1', content, count=1)
            else:
                logging.error("</Extensions> tag not found in autounattend.xml. Cannot append new script.")

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

    # Remove empty settings passes to clean up autounattend.xml
    passes_to_remove = ['offlineServicing', 'generalize', 'auditSystem', 'auditUser']
    for pass_name in passes_to_remove:
        # Match e.g. `<settings pass="offlineServicing"></settings>` on a line and remove it with leading whitespace
        empty_pass_pattern = r'^[ \t]*<settings pass="' + re.escape(pass_name) + r'"></settings>[\r\n]*'
        content = re.sub(empty_pass_pattern, '', content, flags=re.MULTILINE)

    xml_path.write_text(content, encoding='utf-8')

    logging.info("autounattend.xml updated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build and update autounattend.xml with scripts and optional WiFi settings.")
    parser.add_argument('--wifi-ssid', help='SSID for the WiFi network')
    parser.add_argument('--wifi-pass', help='Password for the WiFi network')

    args = parser.parse_args()

    update_autounattend(ssid=args.wifi_ssid, password=args.wifi_pass)
