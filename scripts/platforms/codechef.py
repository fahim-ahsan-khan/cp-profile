import json
import re

import requests

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; cpprofile/1.0; +https://github.com/)",
    "Accept": "text/html,application/xhtml+xml",
}


def _rating_rows(html: str) -> list[dict]:
    match = re.search(
        r'"date_versus_rating":\s*\{\s*"all":\s*(\[.*?\])\s*,\s*"all_old"',
        html,
        re.DOTALL,
    )
    if not match:
        raise ValueError("CodeChef profile: rating history not found")
    return json.loads(match.group(1))


def _contests_from_rows(rows: list[dict], html: str) -> list[dict]:
    shift_match = re.search(
        r'"rating_shift_to_elo_rating_code"\s*:\s*"([^"]+)"',
        html,
    )
    shift_code = shift_match.group(1) if shift_match else None
    contests = []
    for row in rows:
        code = row.get("code")
        if shift_code and code == shift_code:
            continue
        end_date = row.get("end_date") or ""
        if len(end_date) >= 10:
            day = end_date[:10]
        else:
            try:
                y = int(row.get("getyear", 0))
                m = int(row.get("getmonth", 0))
                d = int(row.get("getday", 0))
                day = f"{y:04d}-{m:02d}-{d:02d}"
            except (TypeError, ValueError):
                day = ""
        try:
            rating = int(row.get("rating", 0))
        except (TypeError, ValueError):
            rating = 0
        contests.append(
            {
                "date": day,
                "rating": rating,
                "name": row.get("name", ""),
            }
        )
    return contests


def _solved_from_html(html: str) -> int:
    match = re.search(r"Total Problems Solved:\s*(\d+)", html, re.IGNORECASE)
    return int(match.group(1)) if match else 0


def _rating_from_html(html: str) -> tuple[int, int]:
    current = 0
    max_rating = 0
    m = re.search(
        r'class="rating-number"[^>]*>\s*(\d+)\s*</div>',
        html,
        re.IGNORECASE,
    )
    if m:
        current = int(m.group(1))
    m_max = re.search(r"Highest Rating\s*(\d+)", html, re.IGNORECASE)
    if m_max:
        max_rating = int(m_max.group(1))
    return current, max_rating


def fetch_codechef(username: str) -> dict:
    url = f"https://www.codechef.com/users/{username}"
    solved = 0
    contests: list[dict] = []
    rating = 0
    max_rating = 0

    try:
        res = requests.get(url, headers=_HEADERS, timeout=45)
        res.raise_for_status()
        html = res.text

        solved = _solved_from_html(html)
        rating, max_rating = _rating_from_html(html)

        rows = _rating_rows(html)
        contests = _contests_from_rows(rows, html)

        if contests and not rating:
            rating = contests[-1]["rating"]
        if contests and not max_rating:
            max_rating = max(c["rating"] for c in contests)

        print(f"CodeChef solved: {solved}, contests: {len(contests)}, rating: {rating}")

    except Exception as e:
        print(f"CodeChef fetch failed: {e}")

    return {
        "handle": username,
        "rating": rating,
        "max_rating": max_rating,
        "solved": solved,
        "contests": contests,
    }
