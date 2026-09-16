from agent.workspace import resolve_path


def write_file(path: str, content: str) -> str:
    """
    Write a new file after explicit user confirmation.
    """

    try:
        file_path = resolve_path(path)
    except PermissionError as e:
        return str(e)

    if file_path.exists():
        return (
            f"ERROR: {path} already exists. "
            "Use edit_file instead of write_file."
        )

    print("\n" + "=" * 60)
    print(f"FILE CREATION REQUEST: {path}")
    print("=" * 60)

    print(content)

    print("=" * 60)

    approval = input("Create this file? [y/N]: ").strip().lower()

    if approval != "y":
        return "User rejected file creation."

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_text(
            content,
            encoding="utf-8",
        )

        return f"Successfully created {file_path}."

    except Exception as e:
        return f"Error creating {path}: {e}"