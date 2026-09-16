import subprocess


def git_restore(paths: list[str], staged: bool = False) -> str:
    if not paths:
        return "ERROR: No files specified."

    print("\n" + "=" * 60)
    print("GIT RESTORE REQUEST")
    print("=" * 60)

    print("Files:")
    for path in paths:
        print(f"  {path}")

    if staged:
        print("Mode: unstage")
    else:
        print("Mode: restore working-tree files")

    print("=" * 60)

    if not staged:
        print(
            "WARNING: This may discard uncommitted changes "
            "in the selected files."
        )

    approval = input("Continue? [y/N]: ").strip().lower()

    if approval != "y":
        return (
            "USER_DENIED: The user rejected the git restore operation. "
            "Do not retry unless explicitly requested."
        )

    try:
        command = ["git", "restore"]

        if staged:
            command.append("--staged")

        command.extend(["--", *paths])

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"ERROR: {result.stderr.strip()}"

        return "Git restore completed successfully."

    except Exception as e:
        return f"ERROR: {e}"