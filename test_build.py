from build import xml_encode


def test_xml_encode():
    assert xml_encode(None) is None
    assert xml_encode('Normal String') == 'Normal String'
    assert xml_encode('1 & 2') == '1 &amp; 2'
    assert xml_encode('<tag>') == '&lt;tag&gt;'
    assert xml_encode('"quotes"') == '&quot;quotes&quot;'
    assert xml_encode('<>&"') == '&lt;&gt;&amp;&quot;'
