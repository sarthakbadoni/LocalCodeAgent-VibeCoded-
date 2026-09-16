import subprocess


def git_log(limit: int = 10) -> str:
    try:
        limit = max(1, min(int(limit), 50))

        result = subprocess.run(
            [
                "git",
                "log",
                f"-{limit}",
                "--oneline",
                "--decorate",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"ERROR: {result.stderr.strip()}"

        return result.stdout.strip() or "No commits found."

    except Exception as e:
        return f"ERROR: {e}"