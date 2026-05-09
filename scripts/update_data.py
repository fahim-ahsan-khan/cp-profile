import requests
import json

HANDLE = "loop_breaker"
LEETCODE_USERNAME = "loop_breaker"

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
    }
}

with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated data.json successfully!")
