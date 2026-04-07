from __future__ import annotations

import httpx
from bs4 import BeautifulSoup


def fetch_and_extract_text(url: str) -> str:
    with httpx.Client(timeout=10.0, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())

