import tempfile
import unittest
from pathlib import Path

from agent.memory import MemoryManager


class ThreadMemoryTest(unittest.TestCase):
    def test_exact_tool_call_content_survives_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            memory_path = Path(directory) / "memory.json"
            memory = MemoryManager(memory_path)
            transcript = [
                {"role": "user", "content": "Create the dashboard."},
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "write_file",
                                "arguments": {
                                    "path": "finance_dashboard.html",
                                    "content": "<main>Dashboard</main>",
                                },
                            }
                        }
                    ],
                },
                {
                    "role": "tool",
                    "tool_name": "write_file",
                    "content": "Successfully created /workspace/finance_dashboard.html.",
                },
                {"role": "assistant", "content": "The dashboard is ready."},
            ]

            memory.add_turn(
                "Create the dashboard.",
                "The dashboard is ready.",
                transcript,
            )

            reloaded = MemoryManager(memory_path)
            tool_message = reloaded.data["thread_history"][1]
            content = tool_message["tool_calls"][0]["function"]["arguments"]["content"]

            self.assertEqual(content, "<main>Dashboard</main>")
            self.assertEqual(
                reloaded.data["thread_history"][2]["content"],
                "Successfully created /workspace/finance_dashboard.html.",
            )


if __name__ == "__main__":
    unittest.main()
