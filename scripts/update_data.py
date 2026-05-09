import json
import re
import requests
from bs4 import BeautifulSoup

HANDLE = "loop_breaker"
LEETCODE_USERNAME = "loop_breaker"
BEECROWD_ID = "74808"
UVA_USERNAME = "loop_breaker"

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
# CODEFORCES SUBMISSIONS
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
# LEETCODE
# =========================

leetcode_query = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    username

    submitStats {
      acSubmissionNum {
        difficulty
        count
      }
    }

    profile {
      ranking
    }
  }
}
"""

leetcode_variables = {
    "username": LEETCODE_USERNAME
}

leetcode_response = requests.post(
    "https://leetcode.com/graphql",
    json={
        "query": leetcode_query,
        "variables": leetcode_variables
    }
).json()

matched_user = leetcode_response["data"]["matchedUser"]

stats = matched_user["submitStats"]["acSubmissionNum"]

leetcode_data = {
    "easy": 0,
    "medium": 0,
    "hard": 0,
    "total": 0
}

for item in stats:
    diff = item["difficulty"].lower()
    count = item["count"]

    if diff == "easy":
        leetcode_data["easy"] = count
    elif diff == "medium":
        leetcode_data["medium"] = count
    elif diff == "hard":
        leetcode_data["hard"] = count
    elif diff == "all":
        leetcode_data["total"] = count

leetcode_ranking = matched_user["profile"]["ranking"]

# =========================
# UVA (via uhunt public API)
# =========================
uva_solved = 0
try:
    uid_res = requests.get(
        f"https://uhunt.onlinejudge.org/api/uname2uid/{UVA_USERNAME}",
        timeout=10
    )
    uid = uid_res.json()
    if uid and uid != 0:
        subs_res = requests.get(
            f"https://uhunt.onlinejudge.org/api/subs-user/{uid}",
            timeout=30
        )
        subs_data = subs_res.json()
        # Each submission: [sid, pid, verdict, runtime, time, rank, lang, uacc]
        # verdict 90 = Accepted
        uva_ac_problems = set()
        for sub in subs_data:
            if sub[2] == 90:
                uva_ac_problems.add(sub[1])
        uva_solved = len(uva_ac_problems)
        print(f"UVa solved: {uva_solved}")
    else:
        print(f"UVa username '{UVA_USERNAME}' not found")
except Exception as e:
    print(f"UVa fetch failed: {e}")


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
    },

    "leetcode": {
        "handle": LEETCODE_USERNAME,
        "solved": leetcode_data["total"],
        "easy": leetcode_data["easy"],
        "medium": leetcode_data["medium"],
        "hard": leetcode_data["hard"],
        "ranking": leetcode_ranking
    },

    "uva": {
        "username": UVA_USERNAME,
        "solved": uva_solved
    }
}

with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated data.json successfully!")
