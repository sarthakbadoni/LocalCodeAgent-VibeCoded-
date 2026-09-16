import unittest
from pathlib import Path

import agent.agent as agent_module


class UiDesignModeTest(unittest.TestCase):
    def test_ui_design_rules_are_included(self):
        tool_names = [tool["function"]["name"] for tool in agent_module.tools]
        self.assertIn("search_web", tool_names)

        source_text = Path(agent_module.__file__).read_text()
        system_prompt = source_text

        self.assertIn("UI", system_prompt)
        self.assertIn("design", system_prompt.lower())
        self.assertIn("golden ratio", system_prompt.lower())
        self.assertIn("color palette", system_prompt.lower())
        self.assertIn("search_web", system_prompt.lower())


if __name__ == "__main__":
    unittest.main()
