import requests

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

_BASE = "https://www.hackerrank.com/rest/hackers"


def _badges(username: str) -> list[dict]:
    res = requests.get(f"{_BASE}/{username}/badges", headers=_HEADERS, timeout=30)
    res.raise_for_status()
    body = res.json()
    return body.get("models", []) if isinstance(body, dict) else []


def _scores_elo(username: str) -> list[dict]:
    res = requests.get(f"{_BASE}/{username}/scores_elo", headers=_HEADERS, timeout=30)
    res.raise_for_status()
    body = res.json()
    return body if isinstance(body, list) else []


def _submission_histories(username: str) -> dict:
    res = requests.get(
        f"{_BASE}/{username}/submission_histories",
        headers=_HEADERS,
        timeout=30,
    )
    res.raise_for_status()
    body = res.json()
    return body if isinstance(body, dict) else {}


def _rating_history(username: str) -> list[dict]:
    res = requests.get(
        f"{_BASE}/{username}/rating_histories_elo",
        headers=_HEADERS,
        timeout=30,
    )
    res.raise_for_status()
    body = res.json()
    if not isinstance(body, dict):
        return []
    models = body.get("models") or []
    contests: list[dict] = []
    for track in models:
        if not isinstance(track, dict):
            continue
        if track.get("category") != "Algorithms":
            continue
        for ev in track.get("events") or []:
            if not isinstance(ev, dict):
                continue
            date_raw = ev.get("date") or ""
            day = date_raw[:10] if isinstance(date_raw, str) else ""
            try:
                rating = int(round(float(ev.get("rating", 0) or 0)))
            except (TypeError, ValueError):
                rating = 0
            contests.append(
                {
                    "date": day,
                    "rating": rating,
                    "name": ev.get("contest_name", "") or "",
                }
            )
    return contests


def _total_accepted_submissions(history: dict) -> int:
    total = 0
    for v in history.values():
        try:
            total += int(v)
        except (TypeError, ValueError):
            continue
    return total


def _algorithms_rating(scores: list[dict]) -> int:
    for track in scores:
        if track.get("slug") == "algorithms":
            contest = track.get("contest") or {}
            score = contest.get("score")
            if isinstance(score, (int, float)) and score > 0:
                return int(round(score))
    return 0


def _problem_solving_solved(badges: list[dict]) -> int:
    for badge in badges:
        if badge.get("badge_type") == "problem-solving":
            return int(badge.get("solved", 0) or 0)
    return 0


def _sum_all_badge_solved(badges: list[dict]) -> int:
    return sum(int(b.get("solved", 0) or 0) for b in badges)


def _total_stars(badges: list[dict]) -> int:
    return sum(int(b.get("stars", 0) or 0) for b in badges)


def _earned_badges_count(badges: list[dict]) -> int:
    return sum(1 for b in badges if int(b.get("stars", 0) or 0) > 0)


def fetch_hackerrank(username: str) -> dict:
    problem_solving = 0
    badge_solved_sum = 0
    stars = 0
    earned_badges = 0
    algorithms_rating = 0
    accepted_submissions = 0
    contests: list[dict] = []

    try:
        badges = _badges(username)
        problem_solving = _problem_solving_solved(badges)
        badge_solved_sum = _sum_all_badge_solved(badges)
        stars = _total_stars(badges)
        earned_badges = _earned_badges_count(badges)
    except Exception as e:
        print(f"HackerRank badges fetch failed: {e}")

    try:
        scores = _scores_elo(username)
        algorithms_rating = _algorithms_rating(scores)
    except Exception as e:
        print(f"HackerRank scores fetch failed: {e}")

    try:
        history = _submission_histories(username)
        accepted_submissions = _total_accepted_submissions(history)
    except Exception as e:
        print(f"HackerRank submission history fetch failed: {e}")

    try:
        contests = _rating_history(username)
    except Exception as e:
        print(f"HackerRank rating history fetch failed: {e}")

    if contests and not algorithms_rating:
        algorithms_rating = contests[-1]["rating"]

    solved = problem_solving + badge_solved_sum

    print(
        f"HackerRank solved: {solved} "
        f"(problem-solving: {problem_solving} + badge sum: {badge_solved_sum}), "
        f"submissions: {accepted_submissions}, stars: {stars}, "
        f"badges: {earned_badges}, algorithms rating: {algorithms_rating}, "
        f"contests: {len(contests)}"
    )

    return {
        "handle": username,
        "solved": solved,
        "problem_solving": problem_solving,
        "badge_solved_sum": badge_solved_sum,
        "submissions": accepted_submissions,
        "stars": stars,
        "badges": earned_badges,
        "algorithms_rating": algorithms_rating,
        "contests": contests,
    }
