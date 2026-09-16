import shlex
import subprocess


# Commands that are generally safe to run inside the workspace.
SAFE_COMMANDS = {
    "pwd",
    "ls",
    "find",
    "rg",
    "cat",
    "head",
    "tail",
    "file",
    "wc",
    "which",
    "git status",
    "git diff",
    "git log",
    "python --version",
    "python3 --version",
    "pytest",
}


# Commands/patterns that should never be executed automatically.
BLOCKED_PATTERNS = [
    "rm -rf /",
    "rm -rf ~",
    "rm -rf *",
    "sudo ",
    "mkfs",
    "diskutil erase",
    "diskutil partitionDisk",
    "shutdown",
    "reboot",
    "halt",
    ":(){ :|:& };:",
]


def is_blocked(command: str) -> bool:
    command_lower = command.lower().strip()

    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in command_lower:
            return True

    return False


def is_safe(command: str) -> bool:
    """
    Determine whether a command is safe enough
    to execute without confirmation.
    """

    command = command.strip()

    # Simple exact commands.
    if command in SAFE_COMMANDS:
        return True

    # Common read-only commands with arguments.
    try:
        parts = shlex.split(command)
    except ValueError:
        return False

    if not parts:
        return False

    executable = parts[0]

    safe_executables = {
        "pwd",
        "ls",
        "find",
        "rg",
        "cat",
        "head",
        "tail",
        "file",
        "wc",
        "which",
    }

    return executable in safe_executables


def run_command(command: str) -> str:
    """
    Execute a shell command with a permission layer.
    """

    command = command.strip()

    if not command:
        return "ERROR: Empty command."

    # --------------------------------------------------
    # BLOCKED
    # --------------------------------------------------

    if is_blocked(command):
        return (
            "BLOCKED: This command is considered dangerous "
            "and cannot be executed by the agent."
        )

    # --------------------------------------------------
    # SAFE
    # --------------------------------------------------

    if is_safe(command):
        print("\n[Auto-approved safe command]")
        print(f"$ {command}")

    # --------------------------------------------------
    # REQUIRES APPROVAL
    # --------------------------------------------------

    else:
        print("\n" + "=" * 60)
        print("COMMAND EXECUTION REQUEST")
        print("=" * 60)
        print(f"$ {command}")
        print("=" * 60)

        approval = (
            input("Run this command? [y/N]: ")
            .strip()
            .lower()
        )

        if approval != "y":
            return (
                "USER_DENIED: The user rejected this command. "
                "Do not retry the same command unless the user "
                "explicitly requests it."
            )

    # --------------------------------------------------
    # EXECUTE
    # --------------------------------------------------

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=None,
            capture_output=True,
            text=True,
            timeout=120,
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        output_parts = []

        if stdout:
            output_parts.append(
                "STDOUT:\n" + stdout
            )

        if stderr:
            output_parts.append(
                "STDERR:\n" + stderr
            )

        if output_parts:
            output = "\n\n".join(output_parts)
        else:
            output = "(Command produced no output.)"

        if result.returncode == 0:
            status = "COMMAND SUCCEEDED"
        else:
            status = "COMMAND FAILED"

        return (
            f"$ {command}\n\n"
            f"{output}\n\n"
            f"EXIT CODE: {result.returncode}\n"
            f"{status}"
        )

    except subprocess.TimeoutExpired:
        return (
            "ERROR: Command timed out after 120 seconds."
        )

    except Exception as e:
        return f"ERROR executing command: {e}"