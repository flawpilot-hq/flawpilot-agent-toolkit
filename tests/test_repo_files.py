"""Repo-level checks. Run: python3 -m unittest discover -s tests"""
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent


class RepoFileTests(unittest.TestCase):
    def test_workflow_yaml_parses(self):
        """GitHub silently skips a workflow whose YAML does not parse, so CI would never run."""
        files = sorted((REPO / ".github").rglob("*.yml")) + [REPO / ".gitlab-ci.yml"]
        for f in files:
            if f.exists():
                with self.subTest(file=str(f.relative_to(REPO))):
                    self.assertIsInstance(yaml.safe_load(f.read_text(encoding="utf-8")), dict)


if __name__ == "__main__":
    unittest.main()
