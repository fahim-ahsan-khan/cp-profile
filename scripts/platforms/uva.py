import requests


def fetch_uva(username: str) -> dict:
    uva_solved = 0

    try:
        uid_res = requests.get(
            f"https://uhunt.onlinejudge.org/api/uname2uid/{username}",
            timeout=10,
        )
        uid = uid_res.json()

        if uid and uid != 0:
            subs_res = requests.get(
                f"https://uhunt.onlinejudge.org/api/subs-user/{uid}",
                timeout=30,
            )
            subs_data = subs_res.json()

            uva_ac_problems = set()
            for sub in subs_data:
                if sub[2] == 90:
                    uva_ac_problems.add(sub[1])

            uva_solved = len(uva_ac_problems)
            print(f"UVa solved: {uva_solved}")
        else:
            print(f"UVa username '{username}' not found")

    except Exception as e:
        print(f"UVa fetch failed: {e}")

    return {
        "username": username,
        "solved": uva_solved,
    }
