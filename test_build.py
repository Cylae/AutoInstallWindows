from build import xml_encode


def test_xml_encode():
    assert xml_encode('Test & " < >') == 'Test &amp; &quot; &lt; &gt;'
