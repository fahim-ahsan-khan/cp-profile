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
