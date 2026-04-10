from app.services.sse import chunk_text, sse_payload


def test_chunk_text_every_10_chars():
    text = "0123456789ABCDEFGHIJZ"
    chunks = chunk_text(text, 10)
    assert chunks == ["0123456789", "ABCDEFGHIJ", "Z"]


def test_sse_payload_format():
    payload = sse_payload("你好", False)
    assert payload.startswith("data: ")
    assert '"text": "你好"' in payload
    assert '"is_complete": false' in payload
