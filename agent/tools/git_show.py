import subprocess


def git_show(commit: str = "HEAD") -> str:
    try:
        result = subprocess.run(
            ["git", "show", "--stat", "--oneline", commit],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"ERROR: {result.stderr.strip()}"

        return result.stdout.strip()

    except Exception as e:
        return f"ERROR: {e}"