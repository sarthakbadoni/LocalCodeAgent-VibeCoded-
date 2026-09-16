import json
from pathlib import Path
from typing import Any

from agent.workspace import WORKSPACE


DEFAULT_MEMORY_PATH = WORKSPACE / ".agent_memory.json"


class MemoryManager:
    """
    Lightweight, local-first memory layer for the coding agent.

    It stores:
    - recent chat history
    - a compact summary of older conversation turns
    - a structured task object
    - the most recent project snapshot
    """

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else DEFAULT_MEMORY_PATH
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {
                "conversation_history": [],
                "thread_history": [],
                "summary": "No prior conversation summary.",
                "task_memory": {
                    "current_objective": "",
                    "status": "idle",
                    "subtasks": [],
                    "completed": [],
                    "next_action": "",
                    "updated_at": None,
                },
                "project_snapshot": "",
            }

        try:
            with self.path.open("r", encoding="utf-8") as handle:
                loaded = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return {
                "conversation_history": [],
                "summary": "No prior conversation summary.",
                "task_memory": {
                    "current_objective": "",
                    "status": "idle",
                    "subtasks": [],
                    "completed": [],
                    "next_action": "",
                    "updated_at": None,
                },
                "project_snapshot": "",
            }

        return {
            "conversation_history": loaded.get("conversation_history", []),
            "thread_history": loaded.get(
                "thread_history",
                loaded.get("conversation_history", []),
            ),
            "summary": loaded.get("summary", "No prior conversation summary."),
            "task_memory": {
                "current_objective": loaded.get("task_memory", {}).get("current_objective", ""),
                "status": loaded.get("task_memory", {}).get("status", "idle"),
                "subtasks": loaded.get("task_memory", {}).get("subtasks", []),
                "completed": loaded.get("task_memory", {}).get("completed", []),
                "next_action": loaded.get("task_memory", {}).get("next_action", ""),
                "updated_at": loaded.get("task_memory", {}).get("updated_at"),
            },
            "project_snapshot": loaded.get("project_snapshot", ""),
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(self.data, handle, indent=2, ensure_ascii=False)

    @property
    def conversation_history(self) -> list[dict[str, str]]:
        return self.data["conversation_history"]

    def add_turn(
        self,
        user_message: str,
        assistant_content: str,
        transcript: list[dict[str, Any]] | None = None,
    ) -> None:
        turn_messages = transcript or [
            {
                "role": "user",
                "content": user_message,
            },
            {
                "role": "assistant",
                "content": assistant_content or "",
            },
        ]

        self.data["thread_history"].extend(turn_messages)
        self.data["conversation_history"].extend(turn_messages)
        self._compact_history()
        self._update_task_memory(user_message, assistant_content)
        self.save()

    def set_project_snapshot(self, snapshot: str) -> None:
        self.data["project_snapshot"] = snapshot
        self.save()

    def _compact_history(self, max_recent: int = 30) -> None:
        if len(self.data["conversation_history"]) <= max_recent:
            return

        recent = self.data["conversation_history"][-max_recent:]
        older = self.data["conversation_history"][:-max_recent]

        older_text = "\n".join(
            f"{item.get('role', 'unknown')}: {item.get('content', '')}"
            for item in older
            if isinstance(item, dict)
        )

        self.data["summary"] = (
            (self.data.get("summary", "") + "\n\n" if self.data.get("summary") else "")
            + "Earlier conversation summary:\n"
            + older_text[:2000]
        ).strip()

        self.data["conversation_history"] = recent

    def _update_task_memory(self, user_message: str, assistant_content: str) -> None:
        task_memory = self.data["task_memory"]

        user_text = (user_message or "").strip()
        if not user_text:
            return

        objective = task_memory.get("current_objective") or ""
        status = task_memory.get("status") or "idle"

        if not objective:
            objective = user_text[:200]
            task_memory["current_objective"] = objective
            task_memory["status"] = "in_progress"

        if "create" in user_text.lower() or "build" in user_text.lower():
            task_memory["current_objective"] = user_text[:200]
            task_memory["status"] = "in_progress"

        if "fix" in user_text.lower() or "repair" in user_text.lower() or "debug" in user_text.lower():
            task_memory["status"] = "in_progress"

        if assistant_content and "success" in assistant_content.lower():
            task_memory["status"] = "completed"

        task_memory["next_action"] = (
            "Continue the current task" if task_memory["status"] == "in_progress" else "Review outcome and next step"
        )
        task_memory["updated_at"] = "now"

    def build_context(self, project_context: str) -> list[dict[str, str]]:
        context_messages = [
            {
                "role": "system",
                "content": "Current project context:\n" + project_context,
            },
            {
                "role": "system",
                "content": "Current task memory:\n"
                + json.dumps(self.data["task_memory"], ensure_ascii=False, indent=2),
            },
            {
                "role": "system",
                "content": "Conversation summary:\n" + self.data.get("summary", "No prior conversation summary."),
            },
            {
                "role": "system",
                "content": (
                    "Recent exact thread transcript. Preserve and reuse code "
                    "from this transcript when the user refers to earlier work."
                ),
            },
            *self.data["conversation_history"],
        ]
        return context_messages
