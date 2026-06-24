import os
from personalize import (
    xml_encode,
    get_current_value,
    update_value,
    apply_personalizations
)


def test_xml_encode():
    assert xml_encode('Test & " < >') == 'Test &amp; &quot; &lt; &gt;'
    assert xml_encode(None) is None


def test_get_current_value():
    xml = '<User><Username>Admin</Username></User>'
    assert get_current_value(xml, r'<Username>(.*?)</Username>') == 'Admin'
    assert get_current_value(xml, r'<Password>(.*?)</Password>') == ''


def test_update_value():
    xml = '<User><Username>Admin</Username></User>'
    updated = update_value(
        xml,
        r'(<Username>)(.*?)(</Username>)',
        'Jules'
    )
    assert '<Username>Jules</Username>' in updated


def test_apply_personalizations(tmp_path):
    f = tmp_path / "autounattend.xml"
    content = (
        '<settings pass="specialize"><component name="Microsoft-Windows-'
        'Shell-Setup"><ComputerName>PC</ComputerName></component>'
        '</settings><LocalAccount><Name>A</Name></LocalAccount>'
    )
    settings = {'username': 'Jules', 'computer_name': 'JulesPC'}
    # the function runs subprocess 'build.py'. So create it.
    (tmp_path / "build.py").write_text("print('fake build')")

    old_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        apply_personalizations(f, content, settings)
    finally:
        os.chdir(old_cwd)

    updated = f.read_text()
    assert '<Name>Jules</Name>' in updated
    assert '<ComputerName>JulesPC</ComputerName>' in updated
