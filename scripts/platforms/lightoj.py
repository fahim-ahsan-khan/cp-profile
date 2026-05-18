import requests

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def _int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def fetch_lightoj(username: str) -> dict:
    solved = 0
    tried = 0
    submissions = 0
    accepted = 0
    wrong = 0
    tle = 0
    rte = 0
    ce = 0
    name = ""

    try:
        res = requests.get(
            f"https://lightoj.com/api/v1/users/{username}",
            headers=_HEADERS,
            timeout=30,
        )
        res.raise_for_status()
        body = res.json()

        data = body.get("data") or {}
        user = data.get("user") or {}
        stat = data.get("userStat") or {}

        name = user.get("userNameStr") or ""
        solved = _int(stat.get("isSolved"))
        tried = _int(stat.get("isTried"))
        submissions = _int(stat.get("numSubmissions"))
        accepted = _int(stat.get("numACSubmissions"))
        wrong = _int(stat.get("numWASubmissions"))
        tle = _int(stat.get("numTLESubmissions"))
        rte = _int(stat.get("numRTESubmissions"))
        ce = _int(stat.get("numCESubmissions"))

        print(
            f"LightOJ solved: {solved}, tried: {tried}, "
            f"submissions: {submissions} (AC: {accepted})"
        )
    except Exception as e:
        print(f"LightOJ fetch failed: {e}")

    return {
        "handle": username,
        "name": name,
        "solved": solved,
        "tried": tried,
        "submissions": submissions,
        "ac": accepted,
        "wa": wrong,
        "tle": tle,
        "rte": rte,
        "ce": ce,
    }
