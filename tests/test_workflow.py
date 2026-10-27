import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class WorkflowTest(unittest.TestCase):
    def test_workflow_contract(self):
        y = (ROOT / ".github/workflows/update.yml").read_text()
        for needle in ('cron: "23 4 * * *"', "workflow_dispatch", "contents: write",
                       "python -m gen build --refresh", "secrets.GITHUB_TOKEN",
                       "git diff --cached --quiet"):
            self.assertIn(needle, y)


if __name__ == "__main__":
    unittest.main()
