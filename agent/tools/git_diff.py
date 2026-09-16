import subprocess


def git_diff() -> str:
    """
    Return the current Git diff for the workspace.
    """

    try:
        result = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return (
                f"ERROR: git diff failed.\n\n"
                f"{result.stderr}"
            )

        if not result.stdout.strip():
            return "No unstaged changes."

        return result.stdout

    except subprocess.TimeoutExpired:
        return "ERROR: git diff timed out."

    except Exception as e:
        return f"ERROR: {e}"