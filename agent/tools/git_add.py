import subprocess


def git_add(paths: list[str]) -> str:
    if not paths:
        return "ERROR: No files specified."

    print("\n" + "=" * 60)
    print("GIT ADD REQUEST")
    print("=" * 60)

    print("Files:")
    for path in paths:
        print(f"  {path}")

    print("=" * 60)

    approval = input("Stage these files? [y/N]: ").strip().lower()

    if approval != "y":
        return (
            "USER_DENIED: The user rejected staging these files. "
            "Do not retry unless explicitly requested."
        )

    try:
        result = subprocess.run(
            ["git", "add", "--", *paths],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return f"ERROR: {result.stderr.strip()}"

        return "Successfully staged the requested files."

    except Exception as e:
        return f"ERROR: {e}"