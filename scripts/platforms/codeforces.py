from datetime import datetime, timezone

import requests


def fetch_codeforces(handle: str) -> dict:
    info_url = f"https://codeforces.com/api/user.info?handles={handle}"
    info = requests.get(info_url).json()
    user = info["result"][0]

    rating = user.get("rating", 0)
    max_rating = user.get("maxRating", 0)
    rank = user.get("rank", "unrated")

    subs_url = f"https://codeforces.com/api/user.status?handle={handle}"
    subs = requests.get(subs_url).json()

    solved = set()
    for sub in subs["result"]:
        if sub.get("verdict") == "OK":
            problem = sub["problem"]
            contest_id = problem.get("contestId", "")
            index = problem.get("index", "")
            solved.add(f"{contest_id}-{index}")

    cf_contests = []
    rating_url = f"https://codeforces.com/api/user.rating?handle={handle}"
    try:
        rating_res = requests.get(rating_url, timeout=30).json()
        if rating_res.get("status") == "OK":
            for row in rating_res.get("result", []):
                ts = row.get("ratingUpdateTimeSeconds")
                try:
                    day = (
                        datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")
                        if ts is not None
                        else ""
                    )
                except (OSError, ValueError, TypeError):
                    day = ""
                cf_contests.append(
                    {
                        "date": day,
                        "rating": row.get("newRating", 0),
                        "name": row.get("contestName", ""),
                    }
                )
        else:
            print(f"Codeforces user.rating: {rating_res.get('comment', rating_res)}")
    except Exception as e:
        print(f"Codeforces rating fetch failed: {e}")

    return {
        "handle": handle,
        "rating": rating,
        "max_rating": max_rating,
        "rank": rank,
        "solved": len(solved),
        "contests": cf_contests,
    }
