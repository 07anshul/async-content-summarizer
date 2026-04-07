from __future__ import annotations

import ssl
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


def fetch_and_extract_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": "async-content-summarizer/1.0"})
    ctx = ssl.create_default_context()
    with urlopen(req, timeout=10.0, context=ctx) as resp:
        raw = resp.read()
        charset = resp.headers.get_content_charset() or "utf-8"

    html = raw.decode(charset, errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())
