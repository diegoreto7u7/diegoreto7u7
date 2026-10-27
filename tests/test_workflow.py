import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class WorkflowTest(unittest.TestCase):
    def test_workflow_contract(self):
        y = (ROOT / ".github/workflows/update.yml").read_text()
        for needle in ('cron: "23 4 * * *"', "workflow_dispatch", "contents: write",
                       "branches: [main]", 'paths: ["gen/**", "fonts/**"]',
                       "concurrency:", "group: update-live-data", "cancel-in-progress: false",
                       "python -m gen build --refresh", "secrets.GITHUB_TOKEN",
                       "git add README.md README.en.md assets data",
                       "git diff --cached --quiet", "git pull --rebase"):
            self.assertIn(needle, y)
        self.assertNotIn("git add -A", y)
        # el pull va justo antes del push, después del commit
        self.assertLess(y.index("git commit"), y.index("git pull --rebase"))
        self.assertLess(y.index("git pull --rebase"), y.index("git push"))


if __name__ == "__main__":
    unittest.main()
