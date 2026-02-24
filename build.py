import re
import os
import argparse

# Helper function to XML encode content
def xml_encode(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    return s

def update_autounattend(ssid=None, password=None):
    xml_path = 'autounattend.xml'
    scripts_dir = 'scripts'

    if not os.path.exists(xml_path):
        print(f"Error: {xml_path} not found.")
        return

    with open(xml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # --- Script Updates and Additions ---
    # Iterate over all files in scripts directory

    for root, dirs, files in os.walk(scripts_dir):
        for file in files:
            if not file.endswith('.ps1'):
                continue

            # Construct the relative path from scripts_dir
            # e.g. scripts/Lib/Helper.ps1 -> Lib/Helper.ps1
            rel_path = os.path.relpath(os.path.join(root, file), scripts_dir)

            # Convert to Windows path style for XML matching
            # e.g. Lib\Helper.ps1
            win_rel_path = rel_path.replace(os.sep, '\\')

            # The full path in XML is C:\Windows\Setup\Scripts\<win_rel_path>
            target_path_str = f"C:\\Windows\\Setup\\Scripts\\{win_rel_path}"

            # Read script content
            script_full_path = os.path.join(root, file)
            with open(script_full_path, 'r', encoding='utf-8') as f:
                script_content = f.read()

            # Prepare encoded content
            encoded_content = xml_encode(script_content)

            # Check if file exists in XML
            # Escape for regex
            escaped_path = re.escape(target_path_str)
            pattern = r'(<File path="' + escaped_path + r'">)(.*?)(</File>)'

            if re.search(pattern, content, re.DOTALL):
                print(f"Updating existing file: {target_path_str}")
                # Replacement function to preserve the surrounding tags
                def replacement(match):
                    return match.group(1) + '\n' + encoded_content.strip() + '\n' + match.group(3)

                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            else:
                print(f"Adding new file: {target_path_str}")
                # Construct new File block
                new_file_block = f'\t\t<File path="{target_path_str}">\n{encoded_content.strip()}\n\t\t</File>\n'

                # Insert before </Extensions>
                ext_end_pattern = r'(</Extensions>)'
                if re.search(ext_end_pattern, content):
                     content = re.sub(ext_end_pattern, lambda m: new_file_block + m.group(1), content, count=1)
                else:
                    print(f"Error: </Extensions> tag not found. Cannot add {target_path_str}.")

    # --- WiFi Injection ---
    if ssid and password:
        print(f"Injecting WiFi Profile for SSID: {ssid}")

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

        specialize_pattern = r'(<settings pass="specialize">)(.*?)(</settings>)'
        match_specialize = re.search(specialize_pattern, content, re.DOTALL)

        if match_specialize:
            specialize_content = match_specialize.group(2)

            wlan_comp_pattern = r'(<component name="Microsoft-Windows-Wlan-Svc".*?>)(.*?)(</component>)'
            match_wlan = re.search(wlan_comp_pattern, specialize_content, re.DOTALL)

            if match_wlan:
                # Component exists, replace its content with our profile
                print("Updating existing Microsoft-Windows-Wlan-Svc component...")
                new_wlan_comp = match_wlan.group(1) + wlan_profile + match_wlan.group(3)
                new_specialize_content = specialize_content.replace(match_wlan.group(0), new_wlan_comp)
            else:
                # Component does not exist, append it to the end of specialize settings
                print("Adding Microsoft-Windows-Wlan-Svc component...")
                wlan_component = f"""
            <component name="Microsoft-Windows-Wlan-Svc" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                {wlan_profile}
            </component>
                """
                new_specialize_content = specialize_content + wlan_component

            # Replace the old specialize content with the new one
            full_replacement = match_specialize.group(1) + new_specialize_content + match_specialize.group(3)
            content = content.replace(match_specialize.group(0), full_replacement)

        else:
            print("Error: <settings pass=\"specialize\"> not found in autounattend.xml. Cannot inject WiFi.")

    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("autounattend.xml updated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build and update autounattend.xml with scripts and optional WiFi settings.")
    parser.add_argument('--wifi-ssid', help='SSID for the WiFi network')
    parser.add_argument('--wifi-pass', help='Password for the WiFi network')

    args = parser.parse_args()

    update_autounattend(ssid=args.wifi_ssid, password=args.wifi_pass)
