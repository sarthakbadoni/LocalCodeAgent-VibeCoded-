import subprocess


def git_branch() -> str:
    try:
        result = subprocess.run(
            [
                "git",
                "branch",
                "--list",
                "--verbose",
                "--no-abbrev",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"ERROR: {result.stderr.strip()}"

        return result.stdout.strip() or "No branches found."

    except Exception as e:
        return f"ERROR: {e}"