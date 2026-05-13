import requests

from config import UVA_USER_ID


def _subs_rows(payload):
    if isinstance(payload, dict) and "subs" in payload:
        return payload["subs"], payload
    if isinstance(payload, list):
        return payload, None
    return [], None


def fetch_uva(username: str) -> dict:
    uva_solved = 0
    uid = None
    meta = None
    display_name = None

    try:
        if UVA_USER_ID is not None:
            uid = UVA_USER_ID
        else:
            uid_res = requests.get(
                f"https://uhunt.onlinejudge.org/api/uname2uid/{username}",
                timeout=10,
            )
            uid = uid_res.json()

        if uid and uid != 0:
            subs_res = requests.get(
                f"https://uhunt.onlinejudge.org/api/subs-user/{uid}",
                timeout=30,
            )
            body = subs_res.json()
            rows, meta = _subs_rows(body)
            if isinstance(meta, dict) and meta.get("name"):
                display_name = meta["name"]

            uva_ac_problems = set()
            for sub in rows:
                if isinstance(sub, (list, tuple)) and len(sub) > 2 and sub[2] == 90:
                    uva_ac_problems.add(sub[1])

            uva_solved = len(uva_ac_problems)
            print(f"UVa solved: {uva_solved} (user id {uid})")
        else:
            print(f"UVa username '{username}' not found on uHunt (set UVA_USER_ID for Online Judge id)")

    except Exception as e:
        print(f"UVa fetch failed: {e}")

    out: dict = {
        "username": username,
        "solved": uva_solved,
    }
    if uid and uid != 0:
        out["user_id"] = int(uid)
    if display_name:
        out["display_name"] = display_name
    return out
