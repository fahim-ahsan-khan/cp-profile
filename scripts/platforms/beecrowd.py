import os
import re

import requests

from config import BEECROWD_PROFILE_ID

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _env_solved_override() -> int | None:
    raw = os.environ.get("BEECROWD_SOLVED", "").strip()
    if not raw:
        return None
    try:
        n = int(raw)
        return n if n >= 0 else None
    except ValueError:
        return None


def _is_cloudflare_challenge(html: str) -> bool:
    if len(html) < 8000 and "Just a moment" in html:
        return True
    return "challenges.cloudflare.com" in html and "cf-chl" in html


def _get_html(url: str) -> str | None:
    try:
        import cloudscraper

        scraper = cloudscraper.create_scraper()
        res = scraper.get(url, headers=_HEADERS, timeout=60)
        if res.status_code == 200 and not _is_cloudflare_challenge(res.text):
            return res.text
    except ImportError:
        pass
    except Exception as e:
        print(f"Beecrowd cloudscraper fetch failed: {e}")

    try:
        res = requests.get(url, headers=_HEADERS, timeout=45)
        res.raise_for_status()
        if _is_cloudflare_challenge(res.text):
            return None
        return res.text
    except Exception as e:
        print(f"Beecrowd fetch failed: {e}")
        return None


def _solved_from_html(html: str) -> int | None:
    patterns = [
        r"<strong[^>]*>\s*(\d+)\s*</strong>\s*[^<]{0,80}Solved",
        r"Solved\s*</[^>]+>\s*<[^>]+>\s*<strong[^>]*>\s*(\d+)\s*</strong>",
        r'class="[^"]*stat[^"]*"[^>]*>.*?(\d+).*?Solved',
        r"Solved[^0-9]{0,40}(\d+)",
        r"Problems\s+Solved[^0-9]*(\d+)",
        r'"solved"\s*:\s*(\d+)',
        r"Resolvidos[^0-9]{0,40}(\d+)",
        r"itemprop=\"solved\"[^>]*content=\"(\d+)\"",
    ]
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE | re.DOTALL)
        if m:
            return int(m.group(1))
    return None


def fetch_beecrowd(profile_id: int | None = None) -> dict:
    pid = profile_id if profile_id is not None else BEECROWD_PROFILE_ID
    url = f"https://judge.beecrowd.com/en/profile/{pid}"
    solved = 0

    html = _get_html(url)
    if html:
        parsed = _solved_from_html(html)
        if parsed is not None:
            solved = parsed
            print(f"Beecrowd solved: {solved} (profile {pid})")
        else:
            print(f"Beecrowd profile {pid}: could not parse solved count from HTML")
    else:
        print(f"Beecrowd profile {pid}: blocked or unreachable (Cloudflare)")

    override = _env_solved_override()
    if override is not None and solved == 0:
        solved = override
        print(f"Beecrowd solved from BEECROWD_SOLVED env: {solved}")

    return {
        "profile_id": pid,
        "url": url,
        "solved": solved,
    }
