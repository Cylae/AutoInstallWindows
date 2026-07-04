import os
import platform
import re
import sys
import subprocess
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    TclError = tk.TclError
except ImportError:
    tk = None
    ttk = None
    messagebox = None

    class TclError(Exception):
        pass


def get_windows_timezone():
    if platform.system() != "Windows":
        return ""
    try:
        result = subprocess.run(
            ["powershell", "-Command", "(Get-TimeZone).Id"],
            capture_output=True,
            text=True,
            check=True)
        return result.stdout.strip()
    except Exception:
        return ""


def get_windows_wifi():
    if platform.system() != "Windows":
        return ""
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            check=True)
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
    return re.sub(
        pattern,
        lambda m: m.group(1) + encoded_value + m.group(3),
        content,
        flags=re.DOTALL)


def apply_personalizations(xml_path, content, data):
    new_username = data.get('username', '')
    new_password = data.get('password', '')
    new_computer_name = data.get('computer_name', '')
    new_timezone = data.get('timezone', '')
    new_ui_language = data.get('ui_language', '')
    new_sys_locale = data.get('sys_locale', '')
    new_user_locale = data.get('user_locale', '')
    new_input_locale = data.get('input_locale', '')
    new_wifi_ssid = data.get('wifi_ssid', '')
    new_wifi_pass = data.get('wifi_pass', '')

    # Update Username
    content = update_value(
        content, r'(<LocalAccount[^>]*>\s*<Name>)([^<]*)(</Name>)',
        new_username)
    content = update_value(
        content, r'(<AutoLogon>\s*<Username>)([^<]*)(</Username>)',
        new_username)

    # Update Password
    content = update_value(
        content,
        r'(<LocalAccount[^>]*>.*?<Password>\s*<Value>)([^<]*)(</Value>)',
        new_password)
    content = update_value(
        content,
        r'(<AutoLogon>.*?<Password>\s*<Value>)([^<]*)(</Value>)',
        new_password)

    # Update Locales
    content = update_value(
        content, r'(<UILanguage>)([^<]*)(</UILanguage>)', new_ui_language)
    content = update_value(
        content, r'(<SystemLocale>)([^<]*)(</SystemLocale>)',
        new_sys_locale)
    content = update_value(
        content, r'(<UserLocale>)([^<]*)(</UserLocale>)', new_user_locale)
    content = update_value(
        content, r'(<InputLocale>)([^<]*)(</InputLocale>)',
        new_input_locale)

    # Update TimeZone and ComputerName in specialize pass
    specialize_pattern = r'(<settings pass="specialize">)(.*?)(</settings>)'
    spec_pass_match = re.search(specialize_pattern, content, re.DOTALL)

    if spec_pass_match:
        spec_pass_content = spec_pass_match.group(2)
        shell_setup_pattern = (
            r'(<component name="Microsoft-Windows-Shell-Setup"[^>]*>)'
            r'(.*?)(</component>)'
        )
        shell_setup_match = re.search(
            shell_setup_pattern, spec_pass_content, re.DOTALL)

        if shell_setup_match:
            inner_content = shell_setup_match.group(2)

            # TimeZone
            if new_timezone:
                if '<TimeZone>' in inner_content:
                    inner_content = update_value(
                        inner_content,
                        r'(<TimeZone>)([^<]*)(</TimeZone>)',
                        new_timezone)
                else:
                    inner_content += (
                        f'\n\t\t\t<TimeZone>{new_timezone}</TimeZone>\n\t\t'
                    )
            else:
                inner_content = re.sub(
                    r'\s*<TimeZone>[^<]*</TimeZone>', '', inner_content)

            # ComputerName
            if new_computer_name:
                if '<ComputerName>' in inner_content:
                    inner_content = update_value(
                        inner_content,
                        r'(<ComputerName>)([^<]*)(</ComputerName>)',
                        new_computer_name)
                else:
                    inner_content += (
                        f'\n\t\t\t<ComputerName>{new_computer_name}'
                        f'</ComputerName>\n\t\t'
                    )
            else:
                inner_content = re.sub(
                    r'\s*<ComputerName>[^<]*</ComputerName>', '',
                    inner_content)

            new_shell_setup = shell_setup_match.group(
                1) + inner_content + shell_setup_match.group(3)
            new_spec_pass_content = re.sub(
                shell_setup_pattern,
                lambda m: new_shell_setup,
                spec_pass_content,
                flags=re.DOTALL)
            content = content.replace(
                spec_pass_match.group(0),
                spec_pass_match.group(1) +
                new_spec_pass_content +
                spec_pass_match.group(3))
        else:
            if new_timezone or new_computer_name:
                new_component = (
                    '\n\t\t<component name="Microsoft-Windows-Shell'
                    '-Setup" processorArchitecture="amd64" '
                    'publicKeyToken="31bf3856ad364e35" language="neutral" '
                    'versionScope="nonSxS">\n'
                )
                if new_timezone:
                    new_component += (
                        f'\t\t\t<TimeZone>{new_timezone}</TimeZone>\n'
                    )
                if new_computer_name:
                    new_component += (
                        f'\t\t\t<ComputerName>{new_computer_name}'
                        f'</ComputerName>\n'
                    )
                new_component += '\t\t</component>'

                content = content.replace(
                    spec_pass_match.group(0),
                    spec_pass_match.group(1) +
                    new_component +
                    spec_pass_content +
                    spec_pass_match.group(3))

    xml_path.write_text(content, encoding="utf-8")

    # Run build.py for scripts and wifi
    build_cmd = [sys.executable, "build.py"]
    if new_wifi_ssid:
        build_cmd.extend(["--wifi-ssid", new_wifi_ssid,
                         "--wifi-pass", new_wifi_pass])

    return subprocess.run(
        build_cmd, check=True, capture_output=True, text=True)


class PersonalizationApp(tk.Tk if tk else object):
    def __init__(self, xml_path, content, defaults):
        super().__init__()

        self.title("Ultimate Windows Autounattend - Personalization Tool")
        self.geometry("600x700")
        self.xml_path = xml_path
        self.content = content
        self.defaults = defaults

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            main_frame,
            text="Windows Installation Personalization",
            font=("Helvetica", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Variables
        self.vars = {
            'username': tk.StringVar(value=self.defaults.get('username', '')),
            'password': tk.StringVar(value=self.defaults.get('password', '')),
            'computer_name': tk.StringVar(
                value=self.defaults.get('computer_name', '')),
            'timezone': tk.StringVar(value=self.defaults.get('timezone', '')),
            'ui_language': tk.StringVar(
                value=self.defaults.get('ui_language', '')),
            'sys_locale': tk.StringVar(
                value=self.defaults.get('sys_locale', '')),
            'user_locale': tk.StringVar(
                value=self.defaults.get('user_locale', '')),
            'input_locale': tk.StringVar(
                value=self.defaults.get('input_locale', '')),
            'wifi_ssid': tk.StringVar(
                value=self.defaults.get('wifi_ssid', '')),
            'wifi_pass': tk.StringVar()
        }

        fields = [
            ("👤 Username", 'username'),
            ("🔑 Password", 'password'),
            ("💻 Computer Name", 'computer_name'),
            ("🌍 Time Zone", 'timezone'),
            ("UI Language (e.g., fr-FR, en-US)", 'ui_language'),
            ("System Locale", 'sys_locale'),
            ("User Locale", 'user_locale'),
            ("Input Locale (e.g., 040c:0000040c)", 'input_locale'),
            ("📡 WiFi SSID", 'wifi_ssid'),
            ("🔐 WiFi Password", 'wifi_pass')
        ]

        row = 1
        for label, var_name in fields:
            ttk.Label(main_frame, text=label).grid(
                row=row, column=0, sticky=tk.W, pady=5, padx=5)

            show_char = "*" if "Password" in label else ""
            entry = ttk.Entry(
                main_frame, textvariable=self.vars[var_name], width=40,
                show=show_char)
            entry.grid(row=row, column=1, sticky=tk.EW, pady=5, padx=5)
            row += 1

        ttk.Button(
            main_frame, text="Save & Build", command=self.save_and_build
        ).grid(row=row, column=0, columnspan=2, pady=30)

        main_frame.columnconfigure(1, weight=1)

    def save_and_build(self):
        data = {
            'username': self.vars['username'].get(),
            'password': self.vars['password'].get(),
            'computer_name': self.vars['computer_name'].get(),
            'timezone': self.vars['timezone'].get(),
            'ui_language': self.vars['ui_language'].get(),
            'sys_locale': self.vars['sys_locale'].get(),
            'user_locale': self.vars['user_locale'].get(),
            'input_locale': self.vars['input_locale'].get(),
            'wifi_ssid': self.vars['wifi_ssid'].get(),
            'wifi_pass': self.vars['wifi_pass'].get()
        }

        try:
            apply_personalizations(self.xml_path, self.content, data)
            messagebox.showinfo("Success", "Personalization complete! "
                                "The autounattend.xml is ready.")
            self.destroy()
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr if e.stderr else "Unknown error"
            messagebox.showerror(
                "Error", "Error running build.py:\n" + err_msg)


def prompt_cli(label, current_value):
    current_display = current_value if current_value else "EMPTY"
    user_input = input(f"{label} [Current: {current_display}]: ").strip()
    if user_input.upper() == "CLEAR":
        return ""
    return user_input if user_input else current_value


def cli_main(xml_path, content, defaults):
    if not sys.stdin.isatty():
        print("Non-interactive environment detected. "
              "Applying defaults automatically...")
        try:
            apply_personalizations(xml_path, content, defaults)
            print("[+] Defaults applied successfully.")
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr if e.stderr else "Unknown error"
            print("\n[-] Error running build.py:\n" + err_msg)
            sys.exit(1)
        return

    print("\n===============================================================")
    print(" 🚀 Ultimate Windows Autounattend - Easy Personalization Tool")
    print("===============================================================")
    print("This tool will configure your USB key to automatically "
          "install Windows")
    print("using your preferred settings. Press Enter to accept "
          "the detected defaults.\n")

    new_username = prompt_cli("👤 Username", defaults.get('username'))
    new_password = prompt_cli("🔑 Password", defaults.get('password'))
    new_computer_name = prompt_cli(
        "💻 Computer Name", defaults.get('computer_name'))
    new_timezone = prompt_cli("🌍 Time Zone", defaults.get('timezone'))

    print("\n--- Advanced Locale Settings ---")
    new_ui_language = prompt_cli(
        "UI Language (e.g., fr-FR, en-US)", defaults.get('ui_language'))
    new_sys_locale = prompt_cli(
        "System Locale (e.g., fr-FR, en-US)", defaults.get('sys_locale'))
    new_user_locale = prompt_cli(
        "User Locale (e.g., fr-FR, en-US)", defaults.get('user_locale'))
    new_input_locale = prompt_cli(
        "Input Locale (e.g., 040c:0000040c)", defaults.get('input_locale'))

    print("\n--- WiFi Configuration ---")
    new_wifi_ssid = prompt_cli(
        "📡 WiFi SSID (leave blank to skip)", defaults.get('wifi_ssid'))
    new_wifi_pass = ""
    if new_wifi_ssid:
        new_wifi_pass = input("🔐 WiFi Password: ").strip()

    data = {
        'username': new_username,
        'password': new_password,
        'computer_name': new_computer_name,
        'timezone': new_timezone,
        'ui_language': new_ui_language,
        'sys_locale': new_sys_locale,
        'user_locale': new_user_locale,
        'input_locale': new_input_locale,
        'wifi_ssid': new_wifi_ssid,
        'wifi_pass': new_wifi_pass
    }

    try:
        apply_personalizations(xml_path, content, data)
        print("\n[+] Personalization complete! The autounattend.xml "
              "is ready for your USB key.")
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr if e.stderr else "Unknown error"
        print("\n[-] Error running build.py:\n" + err_msg)
        sys.exit(1)


def main():
    xml_path = Path("autounattend.xml")
    if not xml_path.exists():
        print(f"Error: {xml_path} not found.")
        sys.exit(1)

    content = xml_path.read_text(encoding="utf-8")

    # Extract current values
    username = get_current_value(
        content, r'<LocalAccount[^>]*>\s*<Name>([^<]*)</Name>')
    password = get_current_value(
        content, r'<LocalAccount[^>]*>.*?<Password>\s*<Value>([^<]*)</Value>')
    ui_language = get_current_value(
        content, r'<UILanguage>([^<]*)</UILanguage>')
    sys_locale = get_current_value(
        content, r'<SystemLocale>([^<]*)</SystemLocale>')
    user_locale = get_current_value(
        content, r'<UserLocale>([^<]*)</UserLocale>')
    input_locale = get_current_value(
        content, r'<InputLocale>([^<]*)</InputLocale>')

    specialize_shell_setup_pattern = (
        r'(<settings pass="specialize">.*?<component name='
        r'"Microsoft-Windows-Shell-Setup"[^>]*>)(.*?)(</component>)'
    )
    specialize_match = re.search(
        specialize_shell_setup_pattern, content, re.DOTALL)

    timezone = ""
    computer_name = ""
    if specialize_match:
        spec_content = specialize_match.group(2)
        timezone = get_current_value(
            spec_content, r'<TimeZone>([^<]*)</TimeZone>')
        computer_name = get_current_value(
            spec_content, r'<ComputerName>([^<]*)</ComputerName>')

    detected_user = os.getlogin() if platform.system() == "Windows" else ""
    detected_pc_name = platform.node() if platform.node() else ""
    detected_tz = get_windows_timezone()
    detected_wifi = get_windows_wifi()

    defaults = {
        'username': username if username else detected_user,
        'password': password,
        'computer_name': computer_name if computer_name else detected_pc_name,
        'timezone': timezone if timezone else detected_tz,
        'ui_language': ui_language,
        'sys_locale': sys_locale,
        'user_locale': user_locale,
        'input_locale': input_locale,
        'wifi_ssid': detected_wifi
    }

    try:
        if tk is None:
            raise ImportError("tkinter is not available")
        # Check if we are running in an environment without a display
        # e.g., SSH without X11. This is a common failure point for Tkinter
        if not os.environ.get('DISPLAY') and platform.system() != "Windows":
            raise TclError("No display available")

        app = PersonalizationApp(xml_path, content, defaults)
        app.mainloop()
    except (TclError, ImportError) as e:
        print(f"GUI not available ({e}). Falling back to CLI mode...")
        try:
            cli_main(xml_path, content, defaults)
        except EOFError:
            print("Error: Interactive input required, but EOF reached. "
                  "Please run this tool in an interactive terminal.")
            sys.exit(1)


if __name__ == "__main__":
    main()
