import requests
import json

HANDLE = "loop_breaker"

# =========================
# CODEFORCES USER INFO
# =========================
info_url = f"https://codeforces.com/api/user.info?handles={HANDLE}"
info = requests.get(info_url).json()

user = info["result"][0]

rating = user.get("rating", 0)
max_rating = user.get("maxRating", 0)
rank = user.get("rank", "unrated")

# =========================
# SUBMISSIONS
# =========================
subs_url = f"https://codeforces.com/api/user.status?handle={HANDLE}"
subs = requests.get(subs_url).json()

solved = set()

for sub in subs["result"]:
    if sub.get("verdict") == "OK":
        problem = sub["problem"]

        contest_id = problem.get("contestId", "")
        index = problem.get("index", "")

        solved.add(f"{contest_id}-{index}")

# =========================
# FINAL JSON
# =========================
data = {
    "codeforces": {
        "handle": HANDLE,
        "rating": rating,
        "max_rating": max_rating,
        "rank": rank,
        "solved": len(solved)
    }
}

with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated data.json successfully!")