import hashlib


def compute_content_hash(*, url: str | None, text: str | None) -> str:
    if url:
        raw = "url:" + url.strip()
    else:
        raw = "text:" + (text or "").strip()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

