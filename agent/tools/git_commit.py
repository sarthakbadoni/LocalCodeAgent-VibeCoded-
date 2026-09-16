import subprocess


def git_commit(message: str) -> str:
    if not message.strip():
        return "ERROR: Commit message cannot be empty."

    print("\n" + "=" * 60)
    print("GIT COMMIT REQUEST")
    print("=" * 60)
    print(f"Message: {message}")
    print("=" * 60)

    approval = input("Create this commit? [y/N]: ").strip().lower()

    if approval != "y":
        return (
            "USER_DENIED: The user rejected the commit. "
            "Do not retry unless explicitly requested."
        )

    try:
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            timeout=60,
        )

        output = result.stdout.strip()

        if result.stderr.strip():
            output += "\n" + result.stderr.strip()

        if result.returncode != 0:
            return f"ERROR: Commit failed.\n{output}"

        return f"Commit created successfully.\n\n{output}"

    except Exception as e:
        return f"ERROR: {e}"