from hexbytes import HexBytes

from app.services.indexer import to_hex_string


def test_to_hex_string_from_hexbytes() -> None:
    result = to_hex_string(HexBytes("0x1234"))

    assert result == "0x1234"


def test_to_hex_string_from_bytes() -> None:
    result = to_hex_string(bytes.fromhex("abcd"))

    assert result == "0xabcd"


def test_to_hex_string_from_prefixed_string() -> None:
    result = to_hex_string("0x5678")

    assert result == "0x5678"


def test_to_hex_string_from_plain_string() -> None:
    result = to_hex_string("5678")

    assert result == "0x5678"


def test_to_hex_string_from_none() -> None:
    result = to_hex_string(None)

    assert result == "0x"