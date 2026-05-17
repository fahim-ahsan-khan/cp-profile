import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_scripts_dir = Path(__file__).resolve().parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from config import CF_HANDLE, CODECHEF_USERNAME, LEETCODE_USERNAME, UVA_USERNAME
from platforms.beecrowd import fetch_beecrowd
from platforms.codechef import fetch_codechef
from platforms.codeforces import fetch_codeforces
from platforms.leetcode import fetch_leetcode
from platforms.uva import fetch_uva


def main() -> None:
    data = {
        "meta": {
            "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "codeforces": fetch_codeforces(CF_HANDLE),
        "leetcode": fetch_leetcode(LEETCODE_USERNAME),
        "codechef": fetch_codechef(CODECHEF_USERNAME),
        "uva": fetch_uva(UVA_USERNAME),
        "beecrowd": fetch_beecrowd(),
    }

    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

    print("Updated data.json successfully!")


if __name__ == "__main__":
    main()
