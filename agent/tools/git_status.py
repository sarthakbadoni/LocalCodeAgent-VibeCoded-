import subprocess


def git_status() -> str:
    try:
        result = subprocess.run(
            ["git", "status", "--short", "--branch"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"ERROR: {result.stderr.strip()}"

        return result.stdout.strip() or "Working tree clean."

    except Exception as e:
        return f"ERROR: {e}"