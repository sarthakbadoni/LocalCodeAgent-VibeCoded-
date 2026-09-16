from agent.workspace import resolve_path


def edit_file(
    path: str,
    old_text: str,
    new_text: str,
) -> str:
    """
    Replace one exact piece of text in an existing file.
    """

    try:
        file_path = resolve_path(path)
    except PermissionError as e:
        return str(e)

    if not file_path.is_file():
        return f"Error: File not found: {path}"

    try:
        content = file_path.read_text(encoding="utf-8")

    except UnicodeDecodeError:
        return f"Error: {path} is not a UTF-8 text file."

    except Exception as e:
        return f"Error reading {path}: {e}"

    occurrences = content.count(old_text)

    if occurrences == 0:
        return "Error: The requested text was not found."

    if occurrences > 1:
        return (
            f"Error: The requested text appears {occurrences} times. "
            "The edit must uniquely identify one location."
        )

    updated_content = content.replace(
        old_text,
        new_text,
        1,
    )

    print("\n" + "=" * 60)
    print(f"FILE EDIT REQUEST: {path}")
    print("=" * 60)

    print("OLD:")
    print(old_text)

    print("\nNEW:")
    print(new_text)

    print("=" * 60)

    approval = input("Apply this edit? [y/N]: ").strip().lower()

    if approval != "y":
        return "User rejected the edit."

    try:
        file_path.write_text(
            updated_content,
            encoding="utf-8",
        )

        return f"Successfully edited {path}."

    except Exception as e:
        return f"Error writing {path}: {e}"