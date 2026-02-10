import os
import re

# Configuration
XML_FILE = 'autounattend.xml'
SCRIPTS_DIR = 'scripts'
TARGET_BASE_PATH = r'C:\Windows\Setup\Scripts'

def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def xml_encode(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    return s

def update_xml_content(xml_content, target_path, new_content):
    # The pattern looks for <File path="...">Content</File>
    # We use non-greedy match for content
    escaped_path = re.escape(target_path)
    pattern = r'(<File path="' + escaped_path + r'">)(.*?)(</File>)'

    match = re.search(pattern, xml_content, re.DOTALL)
    if not match:
        return xml_content, False

    encoded_content = xml_encode(new_content.strip())

    def replacement(m):
        return m.group(1) + '\n' + encoded_content + '\n' + m.group(3)

    new_xml_content = re.sub(pattern, replacement, xml_content, flags=re.DOTALL)
    return new_xml_content, True

def main():
    print(f"Reading {XML_FILE}...")
    xml_content = read_file(XML_FILE)
    if not xml_content:
        return

    updated_count = 0
    missing_in_xml = []

    # Walk through scripts directory
    for root, dirs, files in os.walk(SCRIPTS_DIR):
        for file in files:
            if file.endswith('.ps1'):
                local_path = os.path.join(root, file)

                # Calculate relative path from scripts/
                rel_path = os.path.relpath(local_path, SCRIPTS_DIR)

                # Construct target Windows path
                # Replace forward slashes with backslashes
                windows_rel_path = rel_path.replace(os.sep, '\\')
                target_path = f"{TARGET_BASE_PATH}\\{windows_rel_path}"

                print(f"Processing {local_path} -> {target_path}")

                script_content = read_file(local_path)
                if script_content:
                    xml_content, updated = update_xml_content(xml_content, target_path, script_content)
                    if updated:
                        updated_count += 1
                    else:
                        missing_in_xml.append(target_path)

    # Write updated XML
    with open(XML_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    print(f"\nUpdate complete. {updated_count} scripts updated.")

    if missing_in_xml:
        print("\nWarning: The following scripts were found in the folder but not in the XML:")
        for path in missing_in_xml:
            print(f" - {path}")

if __name__ == "__main__":
    main()
