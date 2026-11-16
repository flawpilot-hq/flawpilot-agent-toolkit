"""Tests for scripts/package_skills.py. Run: python3 -m unittest discover -s tests"""
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import package_skills as p  # noqa: E402

GOOD = REPO / "tests" / "fixtures" / "good"
SKILL = Path("plugins/demo/skills/url-scan/SKILL.md")


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "repo"
        shutil.copytree(GOOD, self.root)
        (self.root / "LICENSE").write_text("Apache-2.0 test license\n")
        git(self.root, "init", "-q")
        git(self.root, "add", "-A")
        self.commit()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def commit(self):
        git(self.root, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "--allow-empty", "-m", "x")

    def build(self, out="dist"):
        return p.build(self.root, self.tmp / out)

    def names(self, zip_name, out="dist"):
        with zipfile.ZipFile(self.tmp / out / zip_name) as zf:
            return sorted(zf.namelist())

    def read(self, zip_name, member):
        with zipfile.ZipFile(self.tmp / "dist" / zip_name) as zf:
            return zf.read(member).decode()

    def frontmatter(self, text):
        return yaml.safe_load(text.split("---\n", 2)[1])

    def test_one_zip_per_skill_and_target(self):
        m = self.build()
        self.assertEqual([s["skill"] for s in m["skills"]], ["url-scan"])
        self.assertTrue((self.tmp / "dist" / "url-scan.zip").exists())
        self.assertTrue((self.tmp / "dist" / "url-scan-claude-web.zip").exists())
        self.assertTrue((self.tmp / "dist" / "flawpilot-agent-toolkit-0.1.0.zip").exists())
        self.assertTrue((self.tmp / "dist" / "manifest.json").exists())

    def test_layout(self):
        self.build()
        self.assertEqual(self.names("url-scan.zip"),
                         ["url-scan/LICENSE", "url-scan/SKILL.md", "url-scan/references/bands.md"])
        self.assertIn("demo/url-scan/SKILL.md", self.names("flawpilot-agent-toolkit-0.1.0.zip"))

    def test_source_zip_keeps_skill_md(self):
        self.build()
        self.assertEqual(self.read("url-scan.zip", "url-scan/SKILL.md"), (self.root / SKILL).read_text())

    def test_claude_web_uses_short_description(self):
        self.build()
        fm = self.frontmatter(self.read("url-scan-claude-web.zip", "url-scan/SKILL.md"))
        self.assertEqual(fm["description"], "Run a FlawPilot URL scan.")
        self.assertEqual(fm["name"], "url-scan")

    def test_deterministic(self):
        self.build("a")
        self.build("b")
        digest = lambda d: {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in (self.tmp / d).iterdir()}  # noqa: E731
        self.assertEqual(digest("a"), digest("b"))

    def test_untracked_and_uncommitted_ignored(self):
        (self.root / "plugins/demo/skills/url-scan/notes.md").write_text("local only")
        (self.root / SKILL).write_text((self.root / SKILL).read_text() + "\nUNCOMMITTED\n")
        self.build()
        self.assertNotIn("url-scan/notes.md", self.names("url-scan.zip"))
        self.assertNotIn("UNCOMMITTED", self.read("url-scan.zip", "url-scan/SKILL.md"))

    def test_missing_short_description_fails(self):
        t = (self.root / SKILL).read_text().replace('metadata:\n  short-description: "Run a FlawPilot URL scan."\n', "")
        (self.root / SKILL).write_text(t)
        git(self.root, "add", "-A")
        self.commit()
        with self.assertRaisesRegex(p.PackageError, "short-description is required"):
            self.build()

    def test_long_short_description_fails(self):
        t = (self.root / SKILL).read_text().replace("Run a FlawPilot URL scan.", "x" * 201)
        (self.root / SKILL).write_text(t)
        git(self.root, "add", "-A")
        self.commit()
        with self.assertRaisesRegex(p.PackageError, "max 200"):
            self.build()

    def test_repo_builds(self):
        """The real repo packages cleanly at HEAD (catches over-long descriptions before a release)."""
        m = p.build(REPO, self.tmp / "repo-dist")
        self.assertGreater(len(m["skills"]), 0)


if __name__ == "__main__":
    unittest.main()
