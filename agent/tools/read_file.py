from agent.workspace import resolve_path


def read_file(path: str) -> str:
    try:
        file_path = resolve_path(path)
    except PermissionError as e:
        return str(e)

    if not file_path.is_file():
        return f"Error: File not found: {path}"

    try:
        return file_path.read_text(encoding="utf-8")

    except UnicodeDecodeError:
        return f"Error: {path} is not a UTF-8 text file."

    except Exception as e:
        return f"Error reading {path}: {e}"