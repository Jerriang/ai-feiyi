import json


def chunk_text(text: str, chunk_size: int = 10) -> list[str]:
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def sse_payload(text: str, is_complete: bool) -> str:
    payload = json.dumps({"text": text, "is_complete": is_complete}, ensure_ascii=False)
    return f"data: {payload}\n\n"
