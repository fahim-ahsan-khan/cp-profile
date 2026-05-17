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
    if "Just a moment" in html and len(html) < 20000:
        return True
    return "challenges.cloudflare.com" in html and "cf-chl" in html


def _fetch_with_curl_cffi(url: str) -> str | None:
    try:
        from curl_cffi import requests as cffi_requests

        res = cffi_requests.get(url, headers=_HEADERS, timeout=60, impersonate="chrome120")
        if res.status_code == 200 and not _is_cloudflare_challenge(res.text):
            return res.text
    except ImportError:
        pass
    except Exception as e:
        print(f"Beecrowd curl_cffi fetch failed: {e}")
    return None


def _fetch_with_cloudscraper(url: str) -> str | None:
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
    return None


def _fetch_with_requests(url: str) -> str | None:
    try:
        res = requests.get(url, headers=_HEADERS, timeout=45)
        res.raise_for_status()
        if _is_cloudflare_challenge(res.text):
            return None
        return res.text
    except Exception as e:
        print(f"Beecrowd requests fetch failed: {e}")
        return None


def _fetch_from_api(profile_id: int) -> int | None:
    token = os.environ.get("BEECROWD_API_TOKEN", "").strip()
    if not token:
        return None
    api_url = f"https://api.beecrowd.com.br/users/profile/{profile_id}"
    try:
        res = requests.get(
            api_url,
            headers={
                "accept": "application/json",
                "authorization": f"Bearer {token}",
            },
            timeout=30,
        )
        if res.status_code != 200:
            print(f"Beecrowd API status {res.status_code}")
            return None
        body = res.json()
        stats = body.get("user", {}).get("statistics", {})
        solved = stats.get("solved")
        return int(solved) if solved is not None else None
    except Exception as e:
        print(f"Beecrowd API fetch failed: {e}")
        return None


def _get_html(url: str) -> str | None:
    for fetcher in (_fetch_with_curl_cffi, _fetch_with_cloudscraper, _fetch_with_requests):
        html = fetcher(url)
        if html:
            return html
    return None


def _solved_from_html(html: str) -> int | None:
    m = re.search(
        r'class="profile-solved-number"[^>]*>\s*([\d,]+)\s*<',
        html,
        re.IGNORECASE,
    )
    if m:
        return int(m.group(1).replace(",", ""))

    patterns = [
        r'class="profile-solved-number"[^>]*>\s*([\d,]+)',
        r"<strong[^>]*>\s*([\d,]+)\s*</strong>\s*[^<]{0,80}Solved",
        r"Solved[^0-9]{0,40}([\d,]+)",
        r'"solved"\s*:\s*(\d+)',
        r"Resolvidos[^0-9]{0,40}([\d,]+)",
    ]
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE | re.DOTALL)
        if m:
            return int(m.group(1).replace(",", ""))
    return None


def fetch_beecrowd(profile_id: int | None = None) -> dict:
    pid = profile_id if profile_id is not None else BEECROWD_PROFILE_ID
    url = f"https://judge.beecrowd.com/en/profile/{pid}"
    solved = 0

    api_solved = _fetch_from_api(pid)
    if api_solved is not None:
        solved = api_solved
        print(f"Beecrowd solved: {solved} (profile {pid}, API)")
    else:
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
