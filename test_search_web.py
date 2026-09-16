import unittest
from unittest.mock import patch

from agent.tools.search_web import search_web


class FakeResponse:
    def __init__(self, body):
        self.body = body.encode("utf-8")

    def read(self):
        return self.body


class SearchWebToolTest(unittest.TestCase):
    @patch("agent.tools.search_web.urllib.request.urlopen")
    def test_search_web_returns_results(self, mock_urlopen):
        html = """
        <html>
          <body>
            <a class="result-link" href="https://example.com/alpha">Alpha result</a>
            <a class="result-link" href="https://example.com/beta">Beta result</a>
          </body>
        </html>
        """
        mock_urlopen.return_value = FakeResponse(html)

        result = search_web("python tutorial", max_results=2)

        self.assertIn("Alpha result", result)
        self.assertIn("https://example.com/alpha", result)
        self.assertIn("Beta result", result)


if __name__ == "__main__":
    unittest.main()
