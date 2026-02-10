import re
import os
import html

# Helper function to XML encode content
def xml_encode(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    return s

def update_autounattend():
    xml_path = 'autounattend.xml'
    scripts_dir = 'scripts'

    if not os.path.exists(xml_path):
        print(f"Error: {xml_path} not found.")
        return

    with open(xml_path, 'r', encoding='utf-8') as f:
        content = f.read()

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
            xml_file_path = f"C:\\Windows\\Setup\\Scripts\\{win_rel_path}"

            # Read script content
            script_path = os.path.join(root, file)
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()

            # Prepare encoded content
            encoded_content = xml_encode(script_content)

            # Regex to replace content
            # Pattern: <File path="...xml_file_path...">Content</File>
            # We use non-greedy match for content
            pattern = r'(<File path="' + re.escape(xml_file_path) + r'">)(.*?)(</File>)'

            if re.search(pattern, content, re.DOTALL):
                print(f"Updating {xml_file_path}...")
                def replacement(match):
                    return match.group(1) + '\n' + encoded_content.strip() + '\n' + match.group(3)

                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            else:
                print(f"Warning: File path {xml_file_path} not found in XML. Skipping.")

    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("autounattend.xml updated successfully.")

if __name__ == "__main__":
    update_autounattend()
