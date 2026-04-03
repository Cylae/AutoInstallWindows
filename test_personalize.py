import pytest
from pathlib import Path
from personalize import xml_encode, get_current_value, update_value, apply_personalizations

def test_personalize_xml_encode():
    assert xml_encode(None) == None
    assert xml_encode('') == ''
    assert xml_encode('A & B') == 'A &amp; B'

def test_get_current_value():
    content = '<LocalAccount><Name>Admin</Name></LocalAccount>'
    assert get_current_value(content, r'<LocalAccount[^>]*>\s*<Name>([^<]*)</Name>') == 'Admin'
    assert get_current_value(content, r'<Missing>([^<]*)</Missing>') == ''
    assert get_current_value(content, r'<Missing>([^<]*)</Missing>', default='Def') == 'Def'

def test_update_value():
    content = '<UILanguage>en-US</UILanguage>'
    pattern = r'(<UILanguage>)([^<]*)(</UILanguage>)'

    updated = update_value(content, pattern, 'fr-FR')
    assert updated == '<UILanguage>fr-FR</UILanguage>'

    # Check that XML encoding is applied
    updated_encoded = update_value(content, pattern, 'a&b')
    assert updated_encoded == '<UILanguage>a&amp;b</UILanguage>'

def test_apply_personalizations(tmp_path, monkeypatch):
    # Setup dummy autounattend.xml and build.py in tmp_path
    dummy_xml = """<root>
    <LocalAccount><Name>OldUser</Name></LocalAccount>
    <AutoLogon><Username>OldUser</Username><Password><Value>oldpass</Value></Password></AutoLogon>
    <UILanguage>en-US</UILanguage>
    <SystemLocale>en-US</SystemLocale>
    <UserLocale>en-US</UserLocale>
    <InputLocale>0409:00000409</InputLocale>
    <settings pass="specialize">
        <component name="Microsoft-Windows-Shell-Setup">
            <TimeZone>Pacific Standard Time</TimeZone>
            <ComputerName>OldPC</ComputerName>
        </component>
    </settings>
</root>"""
    xml_path = tmp_path / "autounattend.xml"
    xml_path.write_text(dummy_xml, encoding="utf-8")

    # Mock subprocess.run so build.py isn't actually called
    def mock_run(cmd, *args, **kwargs):
        class MockResult:
            stdout = ""
            stderr = ""
        return MockResult()

    import subprocess
    monkeypatch.setattr(subprocess, "run", mock_run)

    # Monkeypatch sys.executable so the mock command doesn't crash
    import sys
    monkeypatch.setattr(sys, "executable", "python")

    data = {
        'username': 'NewUser',
        'password': 'newpass',
        'computer_name': 'NewPC',
        'timezone': 'Eastern Standard Time',
        'ui_language': 'fr-FR',
        'sys_locale': 'fr-FR',
        'user_locale': 'fr-FR',
        'input_locale': '040c:0000040c',
        'wifi_ssid': 'MyWifi',
        'wifi_pass': 'WifiPass'
    }

    apply_personalizations(xml_path, dummy_xml, data)

    updated_content = xml_path.read_text(encoding="utf-8")
    assert "<Name>NewUser</Name>" in updated_content
    assert "<Username>NewUser</Username>" in updated_content
    assert "<Value>newpass</Value>" in updated_content
    assert "<ComputerName>NewPC</ComputerName>" in updated_content
    assert "<TimeZone>Eastern Standard Time</TimeZone>" in updated_content
    assert "<UILanguage>fr-FR</UILanguage>" in updated_content
    assert "040c:0000040c" in updated_content
