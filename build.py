import re
from pathlib import Path
import logging
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

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
        logger.error(f"Error: {xml_path} not found.")
        return

    content = xml_path.read_text(encoding='utf-8')

    # --- Script Updates ---
    # Iterate over all files in scripts directory
    for script_file in scripts_dir.rglob('*.ps1'):
        rel_path = script_file.relative_to(scripts_dir)
        win_rel_path = str(rel_path).replace('/', '\\')

        script_content = script_file.read_text(encoding='utf-8')
        encoded_content = xml_encode(script_content)

        target_path_str = f"C:\\Windows\\Setup\\Scripts\\{win_rel_path}"
        escaped_path = re.escape(target_path_str)

        pattern = r'(<File path="' + escaped_path + r'">)(.*?)(</File>)'

        if re.search(pattern, content, re.DOTALL):
            logger.info(f"Updating {target_path_str}...")

            def replacement(match):
                return match.group(
                    1) + '\n' + encoded_content.strip() + '\n' + match.group(3)

            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        else:
            logger.info(
                f"File path {target_path_str} not found in XML. "
                "Appending it...")
            _strip_content = encoded_content.strip()
            new_file_block = (
                f'<File path="{target_path_str}">\n'
                f'{_strip_content}\n</File>'
            )
            extensions_close_pattern = r'(</Extensions>)'
            if re.search(extensions_close_pattern, content):
                content = re.sub(
                    extensions_close_pattern,
                    f'{new_file_block}\n\t\\1',
                    content,
                    count=1)
            else:
                logger.error(
                    "Error: </Extensions> tag not found in autounattend.xml. "
                    "Cannot append new script.")

    # --- WiFi Injection ---
    if ssid and password:
        logger.info(f"Injecting WiFi Profile for SSID: {ssid}")

        safe_ssid = xml_encode(ssid)
        safe_password = xml_encode(password)

        wlan_profile = f"""
            <WLANProfile
                xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
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

        specialize_pattern = (
            r'(<settings pass="specialize">)(.*?)(</settings>)'
        )
        match_specialize = re.search(specialize_pattern, content, re.DOTALL)

        if match_specialize:
            specialize_content = match_specialize.group(2)

            wlan_comp_pattern = (
                r'(<component name="Microsoft-Windows-Wlan-Svc".*?>)'
                r'(.*?)(</component>)'
            )
            match_wlan = re.search(
                wlan_comp_pattern,
                specialize_content,
                re.DOTALL)

            if match_wlan:
                logger.info(
                    "Updating existing "
                    "Microsoft-Windows-Wlan-Svc component...")
                new_wlan_comp = match_wlan.group(
                    1) + wlan_profile + match_wlan.group(3)
                new_specialize_content = re.sub(
                    wlan_comp_pattern,
                    lambda m: new_wlan_comp,
                    specialize_content,
                    flags=re.DOTALL)
            else:
                logger.info("Adding Microsoft-Windows-Wlan-Svc component...")
                wlan_component = f"""
            <component name="Microsoft-Windows-Wlan-Svc"
                processorArchitecture="amd64"
                publicKeyToken="31bf3856ad364e35" language="neutral"
                versionScope="nonSxS"
                xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                {wlan_profile}
            </component>
                """
                new_specialize_content = specialize_content + wlan_component

            full_replacement = match_specialize.group(
                1) + new_specialize_content + match_specialize.group(3)
            content = content.replace(
                match_specialize.group(0), full_replacement)

        else:
            logger.error(
                "Error: <settings pass=\"specialize\"> not found in "
                "autounattend.xml. Cannot inject WiFi.")

    # Remove empty settings passes to clean up autounattend.xml
    passes_to_remove = [
        'offlineServicing',
        'generalize',
        'auditSystem',
        'auditUser']
    for pass_name in passes_to_remove:
        empty_pass_pattern = r'^[ \t]*<settings pass="' + \
            re.escape(pass_name) + r'">[\s]*</settings>[\r\n]*'
        content = re.sub(empty_pass_pattern, '', content, flags=re.MULTILINE)

    xml_path.write_text(content, encoding='utf-8')
    logger.info("autounattend.xml updated successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build and update autounattend.xml with scripts "
        "and optional WiFi settings.")
    parser.add_argument('--wifi-ssid', help='SSID for the WiFi network')
    parser.add_argument('--wifi-pass', help='Password for the WiFi network')

    args = parser.parse_args()

    update_autounattend(ssid=args.wifi_ssid, password=args.wifi_pass)
