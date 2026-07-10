from build import xml_encode


def test_xml_encode():
    assert xml_encode("Test") == "Test"
    assert xml_encode("Test & Test") == "Test &amp; Test"
    assert xml_encode("<Test>") == "&lt;Test&gt;"
    assert xml_encode('"Test"') == "&quot;Test&quot;"
