import os
import platform
import re
import sys
import subprocess
from pathlib import Path


def get_windows_timezone():
    if platform.system() != "Windows":
        return ""
    try:
        result = subprocess.run(["powershell", "-Command", "(Get-TimeZone).Id"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception:
        return ""

def get_windows_wifi():
    if platform.system() != "Windows":
        return ""
    try:
        # Get the first connected SSID
        result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True, check=True)
        for line in result.stdout.split('\n'):
            if " SSID " in line:
                return line.split(":")[1].strip()
    except Exception:
        pass
    return ""


def get_current_value(content, pattern, default=""):
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1)
    return default

def xml_encode(s):
    if not s:
        return s
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    return s

def update_value(content, pattern, new_value):
    encoded_value = xml_encode(new_value)
    return re.sub(pattern, lambda m: m.group(1) + encoded_value + m.group(3), content, flags=re.DOTALL)

def prompt(label, current_value):
    current_display = current_value if current_value else "EMPTY"
    user_input = input(f"{label} [Current: {current_display}]: ").strip()
    if user_input.upper() == "CLEAR":
        return ""
    return user_input if user_input else current_value

def main():
    xml_path = Path("autounattend.xml")
    if not xml_path.exists():
        print(f"Error: {xml_path} not found.")
        sys.exit(1)

    content = xml_path.read_text(encoding="utf-8")

    # Extract current values
    username = get_current_value(content, r'<LocalAccount[^>]*>\s*<Name>([^<]*)</Name>')
    password = get_current_value(content, r'<LocalAccount[^>]*>.*?<Password>\s*<Value>([^<]*)</Value>')
    ui_language = get_current_value(content, r'<UILanguage>([^<]*)</UILanguage>')
    sys_locale = get_current_value(content, r'<SystemLocale>([^<]*)</SystemLocale>')
    user_locale = get_current_value(content, r'<UserLocale>([^<]*)</UserLocale>')
    input_locale = get_current_value(content, r'<InputLocale>([^<]*)</InputLocale>')

    # TimeZone and ComputerName might be under Microsoft-Windows-Shell-Setup in specialize pass
    specialize_shell_setup_pattern = r'(<settings pass="specialize">.*?<component name="Microsoft-Windows-Shell-Setup"[^>]*>)(.*?)(</component>)'
    specialize_match = re.search(specialize_shell_setup_pattern, content, re.DOTALL)

    timezone = ""
    computer_name = ""
    if specialize_match:
        spec_content = specialize_match.group(2)
        timezone = get_current_value(spec_content, r'<TimeZone>([^<]*)</TimeZone>')
        computer_name = get_current_value(spec_content, r'<ComputerName>([^<]*)</ComputerName>')

    print("\n=====================================================================")
    print(" 🚀 Ultimate Windows Autounattend - Easy Personalization Tool")
    print("=====================================================================")
    print("This tool will configure your USB key to automatically install Windows")
    print("using your preferred settings. Press Enter to accept the detected defaults.\n")

    # Auto-detect current machine settings to make reinstalling easier
    detected_user = os.getlogin() if platform.system() == "Windows" else ""
    detected_pc_name = platform.node() if platform.node() else ""
    detected_tz = get_windows_timezone()
    detected_wifi = get_windows_wifi()

    # Pre-fill defaults, prioritizing the current machine's detected state over XML state if empty
    default_user = username if username else detected_user
    default_pc = computer_name if computer_name else detected_pc_name
    default_tz = timezone if timezone else detected_tz

    new_username = prompt("👤 Username", default_user)
    new_password = prompt("🔑 Password", password)
    new_computer_name = prompt("💻 Computer Name", default_pc)
    new_timezone = prompt("🌍 Time Zone", default_tz)

    print("\n--- Advanced Locale Settings ---")
    new_ui_language = prompt("UI Language (e.g., fr-FR, en-US)", ui_language)
    new_sys_locale = prompt("System Locale (e.g., fr-FR, en-US)", sys_locale)
    new_user_locale = prompt("User Locale (e.g., fr-FR, en-US)", user_locale)
    new_input_locale = prompt("Input Locale (e.g., 040c:0000040c, 0409:00000409)", input_locale)

    print("\n--- WiFi Configuration ---")
    new_wifi_ssid = prompt("📡 WiFi SSID (leave blank to skip)", detected_wifi)
    new_wifi_pass = ""
    if new_wifi_ssid:
        new_wifi_pass = input("🔐 WiFi Password: ").strip()

    # --- XML Modifications ---

    # Update Username
    content = update_value(content, r'(<LocalAccount[^>]*>\s*<Name>)([^<]*)(</Name>)', new_username)
    content = update_value(content, r'(<AutoLogon>\s*<Username>)([^<]*)(</Username>)', new_username)

    # Update Password
    content = update_value(content, r'(<LocalAccount[^>]*>.*?<Password>\s*<Value>)([^<]*)(</Value>)', new_password)
    content = update_value(content, r'(<AutoLogon>.*?<Password>\s*<Value>)([^<]*)(</Value>)', new_password)

    # Update Locales
    content = update_value(content, r'(<UILanguage>)([^<]*)(</UILanguage>)', new_ui_language)
    content = update_value(content, r'(<SystemLocale>)([^<]*)(</SystemLocale>)', new_sys_locale)
    content = update_value(content, r'(<UserLocale>)([^<]*)(</UserLocale>)', new_user_locale)
    content = update_value(content, r'(<InputLocale>)([^<]*)(</InputLocale>)', new_input_locale)

    # Update TimeZone and ComputerName in specialize pass
    # We need to ensure Microsoft-Windows-Shell-Setup exists in specialize
    specialize_pattern = r'(<settings pass="specialize">)(.*?)(</settings>)'
    spec_pass_match = re.search(specialize_pattern, content, re.DOTALL)

    if spec_pass_match:
        spec_pass_content = spec_pass_match.group(2)
        shell_setup_pattern = r'(<component name="Microsoft-Windows-Shell-Setup"[^>]*>)(.*?)(</component>)'
        shell_setup_match = re.search(shell_setup_pattern, spec_pass_content, re.DOTALL)

        if shell_setup_match:
            inner_content = shell_setup_match.group(2)

            # TimeZone
            if new_timezone:
                if '<TimeZone>' in inner_content:
                    inner_content = update_value(inner_content, r'(<TimeZone>)([^<]*)(</TimeZone>)', new_timezone)
                else:
                    inner_content += f'\n\t\t\t<TimeZone>{new_timezone}</TimeZone>\n\t\t'
            else:
                inner_content = re.sub(r'\s*<TimeZone>[^<]*</TimeZone>', '', inner_content)

            # ComputerName
            if new_computer_name:
                if '<ComputerName>' in inner_content:
                    inner_content = update_value(inner_content, r'(<ComputerName>)([^<]*)(</ComputerName>)', new_computer_name)
                else:
                    inner_content += f'\n\t\t\t<ComputerName>{new_computer_name}</ComputerName>\n\t\t'
            else:
                inner_content = re.sub(r'\s*<ComputerName>[^<]*</ComputerName>', '', inner_content)

            new_shell_setup = shell_setup_match.group(1) + inner_content + shell_setup_match.group(3)
            new_spec_pass_content = re.sub(shell_setup_pattern, lambda m: new_shell_setup, spec_pass_content, flags=re.DOTALL)
            content = content.replace(spec_pass_match.group(0), spec_pass_match.group(1) + new_spec_pass_content + spec_pass_match.group(3))
        else:
            # Add Microsoft-Windows-Shell-Setup
            if new_timezone or new_computer_name:
                new_component = '\n\t\t<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">\n'
                if new_timezone:
                    new_component += f'\t\t\t<TimeZone>{new_timezone}</TimeZone>\n'
                if new_computer_name:
                    new_component += f'\t\t\t<ComputerName>{new_computer_name}</ComputerName>\n'
                new_component += '\t\t</component>'

                content = content.replace(spec_pass_match.group(0), spec_pass_match.group(1) + new_component + spec_pass_content + spec_pass_match.group(3))

    xml_path.write_text(content, encoding="utf-8")
    print("\n[+] autounattend.xml updated with basic personalizations.")

    # Run build.py for scripts and wifi
    print("\n[+] Running build.py to integrate scripts and WiFi settings...")
    build_cmd = [sys.executable, "build.py"]
    if new_wifi_ssid:
        build_cmd.extend(["--wifi-ssid", new_wifi_ssid, "--wifi-pass", new_wifi_pass])

    try:
        subprocess.run(build_cmd, check=True)
        print("\n[+] Personalization complete! The autounattend.xml is ready for your USB key.")
    except subprocess.CalledProcessError as e:
        print(f"\n[-] Error running build.py: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
