import hashlib
from typing import Optional


def compute_content_hash(*, url: Optional[str], text: Optional[str]) -> str:
    if url:
        raw = "url:" + url.strip()
    else:
        raw = "text:" + (text or "").strip()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def compute_extracted_hash(text: str) -> str:
    normalized = " ".join((text or "").split())
    raw = "content:" + normalized
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

