import json
import re
from bs4 import BeautifulSoup
from curl_cffi import requests

HANDLE = "loop_breaker"
LEETCODE_USERNAME = "loop_breaker"
BEECROWD_ID = "74808"

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
# BEECROWD
# =========================

beecrowd_api_url = f"https://judge.beecrowd.com/api/users/{BEECROWD_ID}"
beecrowd_profile_url = f"https://judge.beecrowd.com/en/profile/{BEECROWD_ID}"

beecrowd_solved = 0

# 1. Try the JSON API endpoint first (clean, no HTML parsing)
try:
    api_response = requests.get(
        beecrowd_api_url,
        impersonate="chrome120",
        headers={"Accept": "application/json"}
    )
    if api_response.status_code == 200:
        api_data = api_response.json()
        print(f"Beecrowd API keys: {list(api_data.keys())}")
        for field in ["problems_solved", "solved_problems", "ac_count", "solved", "accepted"]:
            if field in api_data and api_data[field]:
                beecrowd_solved = int(api_data[field])
                print(f"Beecrowd solved (from API field '{field}'): {beecrowd_solved}")
                break
    else:
        print(f"Beecrowd API blocked! Status: {api_response.status_code}")
except Exception as e:
    print("Beecrowd API failed:", e)

# 2. Fall back to HTML scraping if the API returned 0
if beecrowd_solved == 0:
    try:
        response = requests.get(beecrowd_profile_url, impersonate="chrome120")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            solved_nodes = soup.find_all(string=re.compile("Solved", re.IGNORECASE))
            for node in solved_nodes:
                container = node.parent
                if container and container.parent:
                    text = container.parent.get_text(separator=" ", strip=True)
                    match = re.search(r'Solved.*?(\d+)', text, re.IGNORECASE)
                    if match:
                        beecrowd_solved = int(match.group(1))
                        print(f"Beecrowd solved (from HTML scrape): {beecrowd_solved}")
                        break
        else:
            print(f"Beecrowd profile blocked! Status: {response.status_code}")
    except Exception as e:
        print("Beecrowd HTML scraping failed:", e)

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

    "beecrowd": {
        "id": BEECROWD_ID,
        "solved": beecrowd_solved
    }
}

with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated data.json successfully!")
