from pathlib import Path
import subprocess

from agent.workspace import WORKSPACE


def search_files(query: str) -> str:
    """
    Search for text inside the current workspace.
    """

    if not WORKSPACE.is_dir():
        return "Error: Workspace does not exist."

    try:
        result = subprocess.run(
            [
                "rg",
                "--line-number",
                "--hidden",
                "--glob", "!.git",
                "--glob", "!.venv",
                query,
                str(WORKSPACE),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 1:
            return "No matches found."

        if result.returncode != 0:
            return f"Search error: {result.stderr.strip()}"

        output = result.stdout.strip()

        if not output:
            return "No matches found."

        lines = output.splitlines()

        if len(lines) > 100:
            lines = lines[:100]
            lines.append("\n[Results truncated]")

        return "\n".join(lines)

    except FileNotFoundError:
        return "Error: ripgrep (rg) is not installed."

    except subprocess.TimeoutExpired:
        return "Error: Search timed out."

    except Exception as e:
        return f"Error searching files: {e}"