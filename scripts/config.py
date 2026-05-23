import os


def _uva_user_id() -> int | None:
    raw = os.environ.get("UVA_USER_ID", "833661").strip()
    if not raw:
        return None
    try:
        n = int(raw)
        return n if n > 0 else None
    except ValueError:
        return None


CF_HANDLE = os.environ.get("CF_HANDLE", "loop_breaker")
LEETCODE_USERNAME = os.environ.get("LEETCODE_USERNAME", "loop_breaker")
CODECHEF_USERNAME = os.environ.get("CODECHEF_USERNAME", "loop_breaker")
UVA_USERNAME = os.environ.get("UVA_USERNAME", "loop_breaker")
UVA_USER_ID = _uva_user_id()
HACKERRANK_USERNAME = os.environ.get("HACKERRANK_USERNAME", "loop_breaker")
LIGHTOJ_USERNAME = os.environ.get("LIGHTOJ_USERNAME", "loop_breaker")


def _beecrowd_profile_id() -> int:
    raw = os.environ.get("BEECROWD_PROFILE_ID", "74808").strip()
    try:
        n = int(raw)
        return n if n > 0 else 74808
    except ValueError:
        return 74808


BEECROWD_PROFILE_ID = _beecrowd_profile_id()


def _beecrowd_submissions_override() -> int | None:
    raw = os.environ.get("BEECROWD_SUBMISSIONS", "452").strip()
    if not raw:
        return None
    try:
        n = int(raw)
        return n if n >= 0 else None
    except ValueError:
        return None


BEECROWD_SUBMISSIONS_OVERRIDE = _beecrowd_submissions_override()
