import requests

_LEETCODE_QUERY = """
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


def fetch_leetcode(username: str) -> dict:
    leetcode_response = requests.post(
        "https://leetcode.com/graphql",
        json={"query": _LEETCODE_QUERY, "variables": {"username": username}},
    ).json()

    matched_user = leetcode_response["data"]["matchedUser"]
    stats = matched_user["submitStats"]["acSubmissionNum"]

    leetcode_data = {
        "easy": 0,
        "medium": 0,
        "hard": 0,
        "total": 0,
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

    return {
        "handle": username,
        "solved": leetcode_data["total"],
        "easy": leetcode_data["easy"],
        "medium": leetcode_data["medium"],
        "hard": leetcode_data["hard"],
        "ranking": leetcode_ranking,
    }
