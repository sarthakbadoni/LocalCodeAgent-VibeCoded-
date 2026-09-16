from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[1]


def resolve_path(path: str) -> Path:
    """
    Resolve a path and ensure it stays inside the workspace.
    """

    candidate = Path(path).expanduser()

    if not candidate.is_absolute():
        candidate = WORKSPACE / candidate

    candidate = candidate.resolve()

    try:
        candidate.relative_to(WORKSPACE)
    except ValueError:
        raise PermissionError(
            f"Access denied: {candidate} is outside the workspace."
        )

    return candidate