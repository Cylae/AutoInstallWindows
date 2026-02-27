import re
import html
import argparse
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_script_blocks(scripts_dir):
    """
    Recursively scans the scripts directory and generates XML <File> blocks for each .ps1 file.
    """
    scripts_path = Path(scripts_dir)
    if not scripts_path.exists():
        logger.error(f"Scripts directory not found: {scripts_dir}")
        return ""

    file_blocks = []

    # Sort files for deterministic output
    for script_file in sorted(scripts_path.rglob('*.ps1')):
        try:
            # Read script content
            content = script_file.read_text(encoding='utf-8')

            # HTML escape the content, but we need to ensure quotes are handled correctly if needed.
            # python's html.escape escapes &, <, > and optionally quotes.
            # The previous script manually replaced &, <, >, " -> &amp;, &lt;, &gt;, &quot;
            # html.escape(s, quote=True) does exactly that for " as well.
            encoded_content = html.escape(content, quote=True)

            # Construct the relative path and the target Windows path
            rel_path = script_file.relative_to(scripts_path)
            # Convert to Windows backslashes
            win_rel_path = str(rel_path).replace('/', '\\')
            target_path = f"C:\\Windows\\Setup\\Scripts\\{win_rel_path}"

            # Create the XML block
            block = f'<File path="{target_path}">\n{encoded_content}\n</File>'
            file_blocks.append(block)
            logger.info(f"Processed script: {rel_path} -> {target_path}")

        except Exception as e:
            logger.error(f"Failed to process script {script_file}: {e}")

    return "\n\t\t".join(file_blocks)

def update_autounattend(xml_path, scripts_dir, ssid=None, password=None):
    """
    Updates the autounattend.xml file with scripts and WiFi configuration.
    """
    xml_file = Path(xml_path)
    if not xml_file.exists():
        logger.error(f"XML file not found: {xml_path}")
        return

    try:
        content = xml_file.read_text(encoding='utf-8')
    except Exception as e:
        logger.error(f"Failed to read XML file: {e}")
        return

    # --- Sync Scripts ---
    logger.info("Synchronizing scripts...")

    # Extract <ExtractScript> block
    extract_script_pattern = r'(<ExtractScript>.*?</ExtractScript>)'
    extract_match = re.search(extract_script_pattern, content, re.DOTALL)

    if extract_match:
        extract_script_content = extract_match.group(1)

        # Generate new file blocks
        new_file_blocks = get_script_blocks(scripts_dir)

        # Construct new Extensions block
        new_extensions_content = f"\n\t\t{extract_script_content}\n\t\t{new_file_blocks}\n\t"

        # Replace the content inside <Extensions>
        # We replace the whole inner content of Extensions to ensure clean slate
        extensions_pattern = r'(<Extensions.*?>)(.*?)(</Extensions>)'

        def extensions_replacement(match):
            return f"{match.group(1)}{new_extensions_content}{match.group(3)}"

        content = re.sub(extensions_pattern, extensions_replacement, content, flags=re.DOTALL)
        logger.info("Scripts synchronized successfully.")
    else:
        logger.error("Could not find <ExtractScript> block in autounattend.xml")

    # --- WiFi Injection ---
    if ssid and password:
        logger.info(f"Injecting WiFi Profile for SSID: {ssid}")

        safe_ssid = html.escape(ssid, quote=True)
        safe_password = html.escape(password, quote=True)

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

        # Find specialize pass
        specialize_pattern = r'(<settings pass="specialize">)(.*?)(</settings>)'
        match_specialize = re.search(specialize_pattern, content, re.DOTALL)

        if match_specialize:
            specialize_inner = match_specialize.group(2)

            # Check for existing WLAN component
            wlan_comp_pattern = r'(<component name="Microsoft-Windows-Wlan-Svc".*?>)(.*?)(</component>)'
            match_wlan = re.search(wlan_comp_pattern, specialize_inner, re.DOTALL)

            if match_wlan:
                logger.info("Updating existing Microsoft-Windows-Wlan-Svc component...")
                # Replace content inside component
                def wlan_replacement(m):
                    return f"{m.group(1)}\n{wlan_profile}\n{m.group(3)}"

                new_specialize_inner = re.sub(wlan_comp_pattern, wlan_replacement, specialize_inner, flags=re.DOTALL)
            else:
                logger.info("Adding new Microsoft-Windows-Wlan-Svc component...")
                # Create new component
                new_component = f"""
        <component name="Microsoft-Windows-Wlan-Svc" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            {wlan_profile}
        </component>
"""
                new_specialize_inner = specialize_inner + new_component

            # Update the specialize block in main content
            content = content.replace(match_specialize.group(0), f'{match_specialize.group(1)}{new_specialize_inner}{match_specialize.group(3)}')

        else:
            logger.error('<settings pass="specialize"> not found. Cannot inject WiFi.')

    # --- Cleanup ---
    logger.info("Cleaning up empty settings passes...")
    # Remove empty settings passes like <settings pass="offlineServicing"></settings>
    # Allowing for whitespace between tags
    empty_pass_pattern = r'<settings pass="[^"]+">\s*</settings>'
    content = re.sub(empty_pass_pattern, '', content)

    # Write back to file
    try:
        xml_file.write_text(content, encoding='utf-8')
        logger.info(f"Successfully updated {xml_path}")
    except Exception as e:
        logger.error(f"Failed to write to XML file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build and update autounattend.xml with scripts and optional WiFi settings.")
    parser.add_argument('--wifi-ssid', help='SSID for the WiFi network')
    parser.add_argument('--wifi-pass', help='Password for the WiFi network')
    parser.add_argument('--xml-path', default='autounattend.xml', help='Path to autounattend.xml')
    parser.add_argument('--scripts-dir', default='scripts', help='Path to scripts directory')

    args = parser.parse_args()

    update_autounattend(args.xml_path, args.scripts_dir, ssid=args.wifi_ssid, password=args.wifi_pass)
