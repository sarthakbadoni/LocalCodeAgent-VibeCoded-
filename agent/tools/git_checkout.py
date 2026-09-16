import subprocess


def git_checkout(branch: str) -> str:
    if not branch.strip():
        return "ERROR: Branch name cannot be empty."

    print("\n" + "=" * 60)
    print("GIT CHECKOUT REQUEST")
    print("=" * 60)
    print(f"Branch: {branch}")
    print("=" * 60)

    approval = input("Switch to this branch? [y/N]: ").strip().lower()

    if approval != "y":
        return (
            "USER_DENIED: The user rejected the branch switch. "
            "Do not retry unless explicitly requested."
        )

    try:
        result = subprocess.run(
            ["git", "checkout", branch],
            capture_output=True,
            text=True,
            timeout=60,
        )

        output = result.stdout.strip()

        if result.stderr.strip():
            output += "\n" + result.stderr.strip()

        if result.returncode != 0:
            return f"ERROR: Checkout failed.\n{output}"

        return f"Checkout successful.\n\n{output}"

    except Exception as e:
        return f"ERROR: {e}"