import os
import subprocess


# Directories that should not be included in the project tree.
IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".idea",
    ".vscode",
    "DerivedData",
    "build",
    ".build",
    "dist",
    "target",
}


# Files that can help identify the project.
IMPORTANT_FILES = {
    "README.md",
    "README",
    "README.txt",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "setup.py",
    "setup.cfg",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "Package.swift",
    "Podfile",
    "Podfile.lock",
    "Cargo.toml",
    "go.mod",
    ".gitignore",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
}


def get_project_tree(root: str, max_depth: int = 3) -> list[str]:
    """
    Build a compact project tree.
    """

    results = []

    root_depth = root.rstrip(os.sep).count(os.sep)

    for current_root, dirs, files in os.walk(root):

        # Ignore large/generated/dependency directories.
        dirs[:] = [
            directory
            for directory in dirs
            if directory not in IGNORE_DIRS
        ]

        depth = (
            current_root.rstrip(os.sep).count(os.sep)
            - root_depth
        )

        # Stop descending once the maximum depth is reached.
        if depth >= max_depth:
            dirs[:] = []

        relative_root = os.path.relpath(
            current_root,
            root,
        )

        if relative_root == ".":
            relative_root = ""

        # Directories.
        for directory in sorted(dirs):

            if relative_root:
                results.append(
                    f"{relative_root}/{directory}/"
                )
            else:
                results.append(
                    f"{directory}/"
                )

        # Files.
        for filename in sorted(files):

            if relative_root:
                results.append(
                    f"{relative_root}/{filename}"
                )
            else:
                results.append(filename)

    return results


def detect_project_types(root: str) -> list[str]:
    """
    Detect common project types.
    """

    types = []

    # --------------------------------------------------
    # PYTHON
    # --------------------------------------------------

    if os.path.exists(
        os.path.join(root, "pyproject.toml")
    ):
        types.append("Python")

    if os.path.exists(
        os.path.join(root, "requirements.txt")
    ):
        types.append("Python")

    if os.path.exists(
        os.path.join(root, "setup.py")
    ):
        types.append("Python")

    if os.path.exists(
        os.path.join(root, "setup.cfg")
    ):
        types.append("Python")

    # Detect Python projects without dependency files.
    try:

        for name in os.listdir(root):

            if name.endswith(".py"):
                types.append("Python")
                break

    except OSError:
        pass

    # --------------------------------------------------
    # NODE / JAVASCRIPT
    # --------------------------------------------------

    if os.path.exists(
        os.path.join(root, "package.json")
    ):
        types.append("Node.js / JavaScript")

    # --------------------------------------------------
    # SWIFT
    # --------------------------------------------------

    if os.path.exists(
        os.path.join(root, "Package.swift")
    ):
        types.append("Swift Package")

    # --------------------------------------------------
    # XCODE
    # --------------------------------------------------

    try:

        for name in os.listdir(root):

            if name.endswith(".xcodeproj"):
                types.append("Xcode")

            if name.endswith(".xcworkspace"):
                types.append("Xcode Workspace")

    except OSError:
        pass

    # --------------------------------------------------
    # RUST
    # --------------------------------------------------

    if os.path.exists(
        os.path.join(root, "Cargo.toml")
    ):
        types.append("Rust")

    # --------------------------------------------------
    # GO
    # --------------------------------------------------

    if os.path.exists(
        os.path.join(root, "go.mod")
    ):
        types.append("Go")

    # --------------------------------------------------
    # DOCKER
    # --------------------------------------------------

    if os.path.exists(
        os.path.join(root, "Dockerfile")
    ):
        types.append("Docker")

    if os.path.exists(
        os.path.join(root, "docker-compose.yml")
    ):
        types.append("Docker Compose")

    if os.path.exists(
        os.path.join(root, "docker-compose.yaml")
    ):
        types.append("Docker Compose")

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(types))


def get_git_status(root: str) -> str:
    """
    Get a compact Git status.
    """

    try:

        result = subprocess.run(
            [
                "git",
                "status",
                "--short",
                "--branch",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return "Not a Git repository."

        output = result.stdout.strip()

        if not output:
            return "Working tree clean."

        return output

    except subprocess.TimeoutExpired:
        return "Git status timed out."

    except Exception as e:
        return f"Git status unavailable: {e}"


def get_git_branch(root: str) -> str:
    """
    Get the current Git branch.
    """

    try:

        result = subprocess.run(
            [
                "git",
                "branch",
                "--show-current",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return "Not a Git repository."

        branch = result.stdout.strip()

        return branch if branch else "Detached HEAD"

    except Exception:
        return "Unavailable"


def get_recent_commits(root: str, count: int = 5) -> list[str]:
    """
    Get recent Git commits.
    """

    try:

        result = subprocess.run(
            [
                "git",
                "log",
                f"-{count}",
                "--oneline",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return []

        output = result.stdout.strip()

        if not output:
            return []

        return output.splitlines()

    except Exception:
        return []


def get_directory_summary(root: str) -> dict:
    """
    Count important project items.
    """

    summary = {
        "files": 0,
        "directories": 0,
        "python_files": 0,
        "javascript_files": 0,
        "swift_files": 0,
    }

    try:

        for current_root, dirs, files in os.walk(root):

            dirs[:] = [
                directory
                for directory in dirs
                if directory not in IGNORE_DIRS
            ]

            summary["directories"] += len(dirs)

            for filename in files:

                summary["files"] += 1

                if filename.endswith(".py"):
                    summary["python_files"] += 1

                elif filename.endswith(
                    (".js", ".jsx", ".ts", ".tsx")
                ):
                    summary["javascript_files"] += 1

                elif filename.endswith(".swift"):
                    summary["swift_files"] += 1

    except OSError:
        pass

    return summary


def inspect_project() -> str:
    """
    Inspect the current workspace and provide
    a compact project overview for the AI agent.
    """

    root = os.getcwd()

    output = []

    output.append("=" * 60)
    output.append("PROJECT INSPECTION")
    output.append("=" * 60)

    # --------------------------------------------------
    # ROOT
    # --------------------------------------------------

    output.append("")
    output.append("ROOT:")
    output.append(root)

    # --------------------------------------------------
    # PROJECT TYPES
    # --------------------------------------------------

    project_types = detect_project_types(root)

    output.append("")
    output.append("PROJECT TYPES:")

    if project_types:

        for project_type in project_types:
            output.append(f"- {project_type}")

    else:
        output.append("- No recognized project type")

    # --------------------------------------------------
    # DIRECTORY SUMMARY
    # --------------------------------------------------

    summary = get_directory_summary(root)

    output.append("")
    output.append("PROJECT SUMMARY:")
    output.append(
        f"- Files: {summary['files']}"
    )
    output.append(
        f"- Directories: {summary['directories']}"
    )
    output.append(
        f"- Python files: {summary['python_files']}"
    )
    output.append(
        f"- JavaScript/TypeScript files: "
        f"{summary['javascript_files']}"
    )
    output.append(
        f"- Swift files: {summary['swift_files']}"
    )

    # --------------------------------------------------
    # IMPORTANT FILES
    # --------------------------------------------------

    output.append("")
    output.append("IMPORTANT FILES:")

    found_important = []

    for filename in IMPORTANT_FILES:

        path = os.path.join(
            root,
            filename,
        )

        if os.path.exists(path):
            found_important.append(filename)

    if found_important:

        for filename in sorted(found_important):
            output.append(f"- {filename}")

    else:
        output.append("- None detected")

    # --------------------------------------------------
    # GIT BRANCH
    # --------------------------------------------------

    output.append("")
    output.append("GIT BRANCH:")
    output.append(get_git_branch(root))

    # --------------------------------------------------
    # GIT STATUS
    # --------------------------------------------------

    output.append("")
    output.append("GIT STATUS:")
    output.append(get_git_status(root))

    # --------------------------------------------------
    # RECENT COMMITS
    # --------------------------------------------------

    commits = get_recent_commits(root)

    output.append("")
    output.append("RECENT COMMITS:")

    if commits:

        for commit in commits:
            output.append(f"- {commit}")

    else:
        output.append("- No commits found")

    # --------------------------------------------------
    # PROJECT TREE
    # --------------------------------------------------

    output.append("")
    output.append("PROJECT TREE:")

    tree = get_project_tree(
        root,
        max_depth=3,
    )

    if tree:

        for item in tree[:500]:
            output.append(f"- {item}")

    else:
        output.append("- Empty project")

    if len(tree) > 500:

        output.append(
            f"- ... {len(tree) - 500} additional "
            f"items omitted."
        )

    # --------------------------------------------------
    # FINISH
    # --------------------------------------------------

    output.append("")
    output.append("=" * 60)

    return "\n".join(output)