from ollama import chat
import os
from agent.memory import MemoryManager
from agent.tools import read_file as read_file_module
from agent.tools import search_files as search_files_module
from agent.tools import search_web as search_web_module
from agent.tools import write_file as write_file_module
from agent.tools import edit_file as edit_file_module
from agent.tools import run_command as run_command_module
from agent.tools import git_diff as git_diff_module
from agent.tools import git_status as git_status_module
from agent.tools import git_log as git_log_module
from agent.tools import git_show as git_show_module
from agent.tools import git_add as git_add_module
from agent.tools import git_restore as git_restore_module
from agent.tools import git_commit as git_commit_module
from agent.tools import git_branch as git_branch_module
from agent.tools import git_checkout as git_checkout_module
from agent.tools import inspect_project as inspect_project_module
from agent.config import MODEL
from agent.workspace import resolve_path

MAX_TOOL_CALLS = 20
memory = MemoryManager()
conversation_history = memory.conversation_history


def serialize_message(message) -> dict:
    """Convert an Ollama message or dict into JSON-safe thread history."""
    if isinstance(message, dict):
        serialized = {
            key: value
            for key, value in message.items()
            if key in {"role", "content", "tool_name", "tool_calls"}
        }
        tool_calls = serialized.get("tool_calls")
    else:
        serialized = {
            "role": getattr(message, "role", "assistant"),
            "content": getattr(message, "content", "") or "",
        }
        tool_calls = getattr(message, "tool_calls", None)

    if tool_calls:
        serialized["tool_calls"] = [
            {
                "function": {
                    "name": getattr(call.function, "name", ""),
                    "arguments": getattr(call.function, "arguments", {}),
                }
            }
            for call in tool_calls
        ]

    return serialized


def save_conversation_turn(
    user_message: str,
    assistant_content: str,
    transcript: list[dict] | None = None,
) -> None:
    """
    Persist the latest user/assistant exchange so future requests can use
    conversation context.
    """
    memory.add_turn(user_message, assistant_content, transcript)


def get_project_context() -> str:
    """
    Return a compact, read-only summary of the current workspace so the agent
    can reason about the repo as part of its context window.
    """
    try:
        context = inspect_project_module.inspect_project()
        return context.strip() or "Project context unavailable."
    except Exception as exc:
        return f"Project context unavailable: {exc}"


tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a text file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path relative to the workspace.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": (
                "Search for text inside files in the workspace. "
                "Use this when you need to find where something is implemented."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text or pattern to search for.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "Search the web for public information when the answer is not in the local workspace. "
                "Use this for documentation, public APIs, known error messages, design rules, "
                "color palettes, typography guidance, and visual inspiration."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query to look up on the web.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of search results to return.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Create a new file in the workspace. "
                "The user must approve the creation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path relative to the workspace.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Complete contents of the new file.",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": (
                "Replace one exact piece of text in an existing file. "
                "The user must approve the edit."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path relative to the workspace.",
                    },
                    "old_text": {
                        "type": "string",
                        "description": "Exact existing text to replace.",
                    },
                    "new_text": {
                        "type": "string",
                        "description": "Replacement text.",
                    },
                },
                "required": [
                    "path",
                    "old_text",
                    "new_text",
                ],
            },
        },
    },
    {
    "type": "function",
    "function": {
        "name": "run_command",
        "description": (
            "Execute a shell command in the current workspace. "
            "Use this to run tests, builds, formatters, package commands, "
            "or other development commands. "
            "The user must approve the command before it executes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute.",
                }
            },
            "required": ["command"],
        },
    },
},
{
    "type": "function",
    "function": {
        "name": "git_diff",
        "description": (
            "Show the current unstaged Git changes in the workspace. "
            "Use this to inspect what has changed after editing files."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
},
{
    "type": "function",
    "function": {
        "name": "git_status",
        "description": "Show the current Git repository status.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
},

{
    "type": "function",
    "function": {
        "name": "git_log",
        "description": "Show recent Git commits.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of commits to show.",
                }
            },
        },
    },
},

{
    "type": "function",
    "function": {
        "name": "git_show",
        "description": "Show information about a Git commit.",
        "parameters": {
            "type": "object",
            "properties": {
                "commit": {
                    "type": "string",
                    "description": "Commit hash or reference such as HEAD.",
                }
            },
        },
    },
},

{
    "type": "function",
    "function": {
        "name": "git_add",
        "description": "Stage files for a Git commit. Requires user approval.",
        "parameters": {
            "type": "object",
            "properties": {
                "paths": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Files to stage.",
                }
            },
            "required": ["paths"],
        },
    },
},

{
    "type": "function",
    "function": {
        "name": "git_restore",
        "description": (
            "Restore or unstage Git files. Restoring working-tree "
            "files may discard changes and requires approval."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "paths": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                },
                "staged": {
                    "type": "boolean",
                    "description": "If true, only unstage the files.",
                },
            },
            "required": ["paths"],
        },
    },
},

{
    "type": "function",
    "function": {
        "name": "git_commit",
        "description": "Create a Git commit. Requires user approval.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Commit message.",
                }
            },
            "required": ["message"],
        },
    },
},

{
    "type": "function",
    "function": {
        "name": "git_branch",
        "description": "List local Git branches.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
},

{
    "type": "function",
    "function": {
        "name": "git_checkout",
        "description": (
            "Switch to an existing Git branch. "
            "Requires user approval."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "branch": {
                    "type": "string",
                    "description": "Existing branch name.",
                }
            },
            "required": ["branch"],
        },
    },
},
{
    "type": "function",
    "function": {
        "name": "inspect_project",
        "description": (
            "Inspect the current workspace. "
            "Use this to understand project structure, "
            "project type, important files, and Git state "
            "before performing complex development tasks."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
},
]


def run_agent(user_message: str) -> str:
    print("\n[Agent] Preparing request...", flush=True)

    request_text = user_message.lower()
    needs_project_context = any(
        keyword in request_text
        for keyword in (
            "build",
            "create",
            "make",
            "implement",
            "fix",
            "debug",
            "portfolio",
            "dashboard",
            "website",
            "app",
            "project",
        )
    )
    project_context = get_project_context() if needs_project_context else ""
    if project_context:
        memory.set_project_snapshot(project_context)

    print("[Agent] Asking the model...", flush=True)
    messages = [
        {
            "role": "system",
            "content": (
                "You are LocalCodeAgent, a local coding assistant running entirely "
"through a local Ollama model. "

"Follow a disciplined development workflow. "

"First determine whether the user's task is simple or complex. "

"For simple tasks, do not perform unnecessary project-wide inspection. "
"Use only the tools needed to complete the request. "

"For complex tasks, first understand the request and inspect the "
"project before making substantial changes. "

"Use inspect_project when starting a complex task or when you need "
"to understand the project's structure or type. "

"Use search_files when you do not know which file contains relevant "
"code. "

"Use read_file to inspect relevant files before editing them. "

"When the user refers to code, files, or answers from earlier in the "
"same thread, use the exact recent conversation transcript and tool-call "
"content already provided in context. Do not regenerate or replace prior "
"code unless the user asks for a change. "

"Do not modify files based on guesses when the relevant information "
"can be obtained using tools. "

"When implementing changes, make the smallest reasonable set of "
"edits required to accomplish the task. "

"Use write_file only to create new files. "

"Do not use write_file to replace an existing file. If a file already "
"exists, use read_file to inspect it and edit_file to modify it. "

"Use edit_file to modify existing files. "

"Before editing an existing file, inspect the relevant contents "
"with read_file unless the required contents are already known from "
"a reliable tool result. "

"After making code changes, run the most appropriate validation or "
"test command when possible. "

"Choose exactly one primary validation command for the changed code. "

"Do not run multiple test commands that validate the same change "
"unless the first validation fails, the user explicitly asks for "
"multiple test frameworks, or the project requires multiple "
"independent validation steps. "

"Once the primary validation command succeeds with exit code 0 and "
"its output confirms the requested behavior, consider validation "
"complete. Do not repeat the same validation using another test "
"runner. "

"If validation fails, inspect the failure, determine the likely "
"cause, make a targeted correction, and run the appropriate "
"validation again. "

"Before choosing a test command, inspect the project when necessary "
"to determine which testing framework and project configuration "
"are actually present. "

"For Python projects, check for pytest configuration, pyproject.toml, "
"requirements.txt, or unittest-based tests when determining the "
"appropriate validation command. "

"If the changed Python file contains unittest.TestCase classes or "
"uses the unittest framework, use "
"'python -m unittest <test_file> -v' as the primary validation "
"command. "

"Do not execute a unittest test file directly with "
"'python <test_file>' when unittest is clearly being used, unless "
"the user explicitly requests direct execution. "

"Do not use pytest for unittest tests unless pytest is explicitly "
"configured as the project's test runner or the user explicitly "
"requests pytest. "

"For pytest-based Python projects, use the project's configured "
"pytest command or the simplest appropriate pytest command. "

"For JavaScript or TypeScript projects, inspect package.json and use "
"the project's configured test script when available. "

"For Swift projects, inspect Package.swift, .xcodeproj, or "
".xcworkspace and use the appropriate Swift or Xcode test command. "

"Do not invent complicated test commands when a simpler "
"project-appropriate command is available. "

"Prefer the simplest validation command that reliably tests the "
"changes that were made. "

"Do not run a validation command merely because it is available. "
"Choose the command that best matches the actual test framework "
"and changed code. "

"Do not combine unrelated fallback commands with shell operators "
"such as '||' merely to force a successful result. "

"Do not treat a command as successful merely because it executed. "

"Always inspect the exit code and actual output of a validation "
"command before deciding whether validation passed. "

"Treat any non-zero exit code as a failed command. "

"If a command fails, inspect the failure before deciding what to do "
"next. "

"If the failure is caused by the implementation, make a targeted "
"code correction and validate again. "

"If the failure is caused by the command itself, choose a corrected "
"project-appropriate command rather than changing working code "
"unnecessarily. "

"Continue the repair cycle until the task is complete, validation "
"passes, or the tool-call limit is reached. "

"Do not claim that a task succeeded unless the available tool "
"results support that conclusion. "

"Do not claim that tests passed unless a validation command actually "
"returned exit code 0 and its output supports that conclusion. "

"Do not claim that a file was created, modified, deleted, staged, "
"committed, or restored unless the corresponding tool result "
"confirms that operation. "

"Use run_command to execute development commands. "

"Use git_status to understand repository state. "

"Use git_diff to inspect changes. "

"Use git_log to inspect commit history. "

"Use git_show to inspect a specific commit. "

"Use git_branch to inspect available branches. "

"Use git_add to stage files when appropriate. "

"Use git_commit only when the user explicitly requests a commit. "

"Use git_restore carefully because it can discard changes. "

"Use git_checkout only when the user explicitly requests switching "
"branches. "

"Do not perform Git operations that change repository state unless "
"the user requested the operation or it is clearly required by "
"the user's task. "

"Before creating a commit, inspect Git status when appropriate so "
"you know which changes are being committed. "

"IMPORTANT: If a tool returns USER_DENIED, do not retry the same "
"operation unless the user explicitly requests it. "

"If a tool returns BLOCKED, do not attempt to bypass the restriction. "

"Never attempt to bypass a tool's safety restrictions by modifying "
"the command, using another shell command, or using another tool. "

"When the task is complete, provide a concise summary of what changed "
"and what validation was performed. "

"If the user asks for a project that requires a UI, landing page, "
"dashboard, app interface, portfolio, website, or visual product "
"experience, treat it as a design-first task. "

"Before implementing UI-heavy work, create a concise design brief "
"covering: target audience, product intent, device type, brand tone, "
"layout style, accessibility needs, and visual mood. "

"Use search_web to look up public design rules, color palette "
"references, accessibility guidance, typography systems, spacing "
"patterns, and UI examples when the answer is not already in the "
"workspace. "

"For UI work, prefer design systems with strong hierarchy and clarity. "
"Use balanced spacing, readable typographic scales, consistent "
"alignment, and a restrained color palette. "

"Choose project-appropriate color palettes: SaaS and productivity "
"should favor clean, trustworthy palettes (blues, indigos, neutrals); "
"wellness and health can use softer greens and teals; finance can use "
"deep navy, gold, and neutral tones; luxury brands can use cream, "
"charcoal, muted gold, and minimal contrast; creative brands can use "
"more expressive accent colors when appropriate. "

"Use established design principles such as visual hierarchy, "
"whitespace rhythm, contrast, cohesion, consistency, and alignment. "
"Use a restrained palette of 3-5 colors with one primary accent and "
"one neutral base. "

"Use proportion systems inspired by the golden ratio for layout balance "
"and hero composition when helpful, but do not over-apply it; prefer "
"natural visual balance and usability over decorative math. "

"Use a typographic scale with clear hierarchy: headings, subheadings, "
"body text, labels, and metadata should be visually distinct but "
"consistent. "

"Use a spacing system such as an 8px or 4px scale for padding, gap, "
"and margins. "

"Ensure accessibility: maintain readable contrast, avoid low-contrast "
"text, provide focus states, and keep the interface easy to scan. "

"When generating UI code, the result should feel polished, intentional, "
"and aligned to the product's purpose rather than randomly styled. "

"If validation was not possible, clearly state that validation was "
"not performed and explain why."
            ),
        },
        *memory.build_context(project_context),
        {
            "role": "user",
            "content": user_message,
        },
    ]

    tool_call_count = 0
    recent_tool_calls = set()
    turn_start = len(messages) - 1

    while True:

        if tool_call_count >= MAX_TOOL_CALLS:
            final_response = (
                "I stopped because the maximum number of tool calls "
                f"({MAX_TOOL_CALLS}) was reached. "
                "The task may require another attempt."
            )
            save_conversation_turn(
                user_message,
                final_response,
                [serialize_message(message) for message in messages[turn_start:]],
            )
            return final_response

        response = chat(
            model=MODEL,
            messages=messages,
            tools=tools,
            think=False,
        )

        assistant_message = response.message

        messages.append(assistant_message)

        # --------------------------------------------------
        # FINAL RESPONSE
        # --------------------------------------------------

        if not assistant_message.tool_calls:
            final_response = assistant_message.content or ""
            save_conversation_turn(
                user_message,
                final_response,
                [serialize_message(message) for message in messages[turn_start:]],
            )
            return final_response

        # --------------------------------------------------
        # TOOL CALLS
        # --------------------------------------------------

        for tool_call in assistant_message.tool_calls:

            tool_call_count += 1

            tool_name = tool_call.function.name
            arguments = tool_call.function.arguments
            # --------------------------------------------------
            # DUPLICATE TOOL CALL PROTECTION
            # --------------------------------------------------

            tool_signature = (
                tool_name,
                str(sorted(arguments.items()))
            )

            if tool_signature in recent_tool_calls:
                result = (
                    "ERROR: This exact tool call was already performed. "
                    "Do not repeat the same operation. "
                    "Use the result from the previous tool call instead."
            )

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": tool_name,
                        "content": result,
                    }
                )

                continue

            recent_tool_calls.add(tool_signature)

            print(
                f"\n[Tool {tool_call_count}/{MAX_TOOL_CALLS}: "
                f"{tool_name}]"
            )

            # --------------------------------------------------
            # READ FILE
            # --------------------------------------------------

            if tool_name == "read_file":

                result = read_file_module.read_file(
                    arguments["path"]
                )

            # --------------------------------------------------
            # SEARCH FILES
            # --------------------------------------------------

            elif tool_name == "search_files":

                result = search_files_module.search_files(
                    arguments["query"]
                )

            elif tool_name == "search_web":

                result = search_web_module.search_web(
                    arguments["query"],
                    arguments.get("max_results", 5),
                )

            # --------------------------------------------------
            # WRITE FILE
            # --------------------------------------------------

            elif tool_name == "write_file":

                path = arguments["path"]

                # Prevent the model from overwriting an existing file
                # through write_file. Existing files should be inspected
                # and modified using edit_file instead.
    

                if resolve_path(path).exists():
                    result = (
                        f"ERROR: File '{path}' already exists. "
                        "Do not use write_file for an existing file. "
                        "Use read_file first to inspect it, then use "
                        "edit_file to modify it if necessary."
                    )
                else:
                    result = write_file_module.write_file(
                        path,
                        arguments["content"]
                    )

            # --------------------------------------------------
            # EDIT FILE
            # --------------------------------------------------

            elif tool_name == "edit_file":

                result = edit_file_module.edit_file(
                    arguments["path"],
                    arguments["old_text"],
                    arguments["new_text"],
                )

            # --------------------------------------------------
            # RUN COMMAND
            # --------------------------------------------------

            elif tool_name == "run_command":

                result = run_command_module.run_command(
                    arguments["command"]
                )
            elif tool_name == "git_diff":
                result = git_diff_module.git_diff()


            elif tool_name == "git_status":
                result = git_status_module.git_status()

            elif tool_name == "git_log":
                result = git_log_module.git_log(
                    arguments.get("limit", 10)
                )

            elif tool_name == "git_show":
                result = git_show_module.git_show(
                    arguments.get("commit", "HEAD")
                )

            elif tool_name == "git_add":
                result = git_add_module.git_add(
                    arguments["paths"]
                )

            elif tool_name == "git_restore":
                result = git_restore_module.git_restore(
                    arguments["paths"],
                    arguments.get("staged", False),
                )

            elif tool_name == "git_commit":
                result = git_commit_module.git_commit(
                    arguments["message"]
                )

            elif tool_name == "git_branch":
                result = git_branch_module.git_branch()

            elif tool_name == "git_checkout":
                result = git_checkout_module.git_checkout(
                    arguments["branch"]
                )

            elif tool_name == "inspect_project":
                result = inspect_project_module.inspect_project()

            # --------------------------------------------------
            # UNKNOWN TOOL
            # --------------------------------------------------

            else:

                result = (
                    f"Error: Unknown tool: {tool_name}"
                )

            # --------------------------------------------------
            # SEND TOOL RESULT BACK TO MODEL
            # --------------------------------------------------

            messages.append(
                {
                    "role": "tool",
                    "tool_name": tool_name,
                    "content": result,
                }
            )

            # --------------------------------------------------
            # HANDLE PERMISSION RESULT
            # --------------------------------------------------

            if isinstance(result, str):

                if result.startswith("USER_DENIED:"):
                    final_response = (
                        "The operation was cancelled because "
                        "permission was denied."
                    )
                    save_conversation_turn(
                        user_message,
                        final_response,
                        [serialize_message(message) for message in messages[turn_start:]],
                    )
                    return final_response

                if result.startswith("BLOCKED:"):
                    final_response = (
                        "The operation was blocked by the command "
                        "safety policy."
                    )
                    save_conversation_turn(
                        user_message,
                        final_response,
                        [serialize_message(message) for message in messages[turn_start:]],
                    )
                    return final_response