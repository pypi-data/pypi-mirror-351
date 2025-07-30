from mm_mnemonic.account import is_address_matched


def test_is_address_matched():
    assert is_address_matched("0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7")
    assert is_address_matched("0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "0x35b94EF616D5F83*dEBe49beC8B7A7")
    assert not is_address_matched("0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "0x35b94EF616D5F82*dEBe49beC8B7A7")
    assert is_address_matched("0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "*EBe49beC8B7A7")
    assert is_address_matched("0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "0x35b94EF616*")
    assert is_address_matched("0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "*EBe49beC8B7A7")
    assert not is_address_matched("0x25b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "0x35b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7")
    assert not is_address_matched("0x25b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", None)
    assert not is_address_matched("0x25b94EF616D5F836B8ac27A4e4dEBe49beC8B7A7", "")
