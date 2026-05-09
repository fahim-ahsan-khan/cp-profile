import requests
import json
from bs4 import BeautifulSoup

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
import re  # We need regex for the smarter search 

beecrowd_url = f"https://judge.beecrowd.com/en/profile/{BEECROWD_ID}"

# 1. Disguise the request as a real browser (Fixes the 403 Cloudflare block)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(beecrowd_url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

beecrowd_solved = 0

try:
    if response.status_code == 200:
        # 2. Robust Search: Look for the text "Solved" directly, ignoring HTML tags/classes
        solved_nodes = soup.find_all(string=re.compile("Solved", re.IGNORECASE))
        
        for node in solved_nodes:
            # Traverse slightly up the HTML tree to grab the text and the number next to it safely
            container = node.parent
            if container and container.parent:
                text = container.parent.get_text(separator=" ", strip=True)
                
                # Use Regex to extract the first set of digits that come immediately after "Solved"
                match = re.search(r'Solved.*?(\d+)', text, re.IGNORECASE)
                if match:
                    beecrowd_solved = int(match.group(1))
                    break  # Stop looking once we find the valid number
    else:
        print(f"Beecrowd request blocked! Status Code: {response.status_code}")

except Exception as e:
    print("Beecrowd parsing failed:", e)

# =========================
# FINAL JSON
# =========================

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
