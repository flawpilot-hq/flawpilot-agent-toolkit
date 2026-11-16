#!/usr/bin/env python3
"""Build one ZIP per skill for web uploads (Claude.ai, ChatGPT), from tracked files at a git ref.

Usage: python3 scripts/package_skills.py [--ref REF] [--out DIR] [ROOT]

Targets, per skill:
  <skill>.zip             SKILL.md unchanged. For ChatGPT and any Agent Skills client.
  <skill>-claude-web.zip  description replaced by metadata.short-description (Claude.ai allows 200 chars).
Also writes flawpilot-agent-toolkit-<version>.zip (every skill, unchanged) and manifest.json.

Only files tracked by git at REF are packaged, so local edits and ignored files never ship.
Output is deterministic: the same ref gives byte-identical ZIPs. Needs PyYAML.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import yaml

MAX_DESC = {"source": 1024, "claude-web": 200}
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
EXCLUDE_PARTS = {"__pycache__", "node_modules", ".DS_Store", "evals"}


class PackageError(Exception):
    pass


def git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True).stdout


def tracked_files(root: Path, ref: str) -> dict[str, tuple[str, str]]:
    """Map path -> (mode, blob sha) for every file tracked at ref."""
    out = git(root, "ls-tree", "-r", "-z", ref).decode()
    files = {}
    for rec in filter(None, out.split("\0")):
        meta, path = rec.split("\t", 1)
        mode, kind, sha = meta.split()
        if kind == "blob":
            files[path] = (mode, sha)
    return files


def split_frontmatter(text: str) -> tuple[dict, str, str]:
    """Return (data, raw frontmatter, rest of file after the closing ---)."""
    if not text.startswith("---\n"):
        raise PackageError("SKILL.md must start with ---")
    head, sep, rest = text[4:].partition("\n---\n")
    if not sep:
        raise PackageError("frontmatter is not closed with ---")
    data = yaml.safe_load(head)
    if not isinstance(data, dict):
        raise PackageError("frontmatter must be a YAML mapping")
    return data, head, rest


def render_skill_md(text: str, target: str, where: str) -> str:
    data, head, rest = split_frontmatter(text)
    desc = data.get("description")
    if target == "claude-web":
        short = (data.get("metadata") or {}).get("short-description")
        if not isinstance(short, str) or not short.strip():
            raise PackageError(f"{where}: metadata.short-description is required for the claude-web ZIP")
        lines = head.split("\n")
        idx = [i for i, ln in enumerate(lines) if ln.startswith("description:")]
        if len(idx) != 1:
            raise PackageError(f"{where}: expected one single-line `description:`")
        lines[idx[0]] = "description: " + json.dumps(short, ensure_ascii=False)
        head = "\n".join(lines)
        if yaml.safe_load(head).get("description") != short:
            raise PackageError(f"{where}: could not rewrite description")
        desc = short
    if not isinstance(desc, str) or not desc.strip():
        raise PackageError(f"{where}: description is required")
    if len(desc) > MAX_DESC[target]:
        raise PackageError(f"{where}: {target} description is {len(desc)} characters, max {MAX_DESC[target]}")
    return f"---\n{head}\n---\n{rest}"


def write_zip(path: Path, entries: list[tuple[str, bytes, str]]) -> str:
    """entries: (archive name, data, git mode). Returns sha256 of the ZIP."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for name, data, mode in sorted(entries):
            info = zipfile.ZipInfo(name, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if mode == "100755" else 0o644) << 16
            info.create_system = 3
            zf.writestr(info, data)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(root: Path, out: Path, ref: str = "HEAD") -> dict:
    root = root.resolve()
    files = tracked_files(root, ref)
    blob = lambda p: git(root, "cat-file", "blob", files[p][1])  # noqa: E731
    if "LICENSE" not in files:
        raise PackageError("LICENSE is not tracked at " + ref)
    license_bytes = blob("LICENSE")

    skills: dict[str, dict] = {}
    for path in sorted(files):
        parts = path.split("/")
        if len(parts) == 5 and parts[0] == "plugins" and parts[2] == "skills" and parts[4] == "SKILL.md":
            plugin, skill = parts[1], parts[3]
            if skill in skills:
                raise PackageError(f"skill name {skill!r} is used by two plugins")
            version = json.loads(blob(f"plugins/{plugin}/.claude-plugin/plugin.json"))["version"]
            skills[skill] = {"plugin": plugin, "version": version, "dir": "/".join(parts[:4])}
    if not skills:
        raise PackageError("no skills found under plugins/*/skills/")
    versions = {s["version"] for s in skills.values()}
    if len(versions) != 1:
        raise PackageError(f"plugins disagree on version: {sorted(versions)}")
    version = versions.pop()

    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.zip"):
        old.unlink()
    manifest = {"version": version, "ref": git(root, "rev-parse", ref).decode().strip(), "skills": []}
    bundle: list[tuple[str, bytes, str]] = []
    for skill, info in sorted(skills.items()):
        prefix = info["dir"] + "/"
        members = [p for p in files if p.startswith(prefix) and not (set(p.split("/")) & EXCLUDE_PARTS)]
        base: list[tuple[str, bytes, str]] = []
        skill_md = ""
        for p in members:
            data = blob(p)
            if p == prefix + "SKILL.md":
                skill_md = data.decode("utf-8")
            base.append((skill + "/" + p[len(prefix):], data, files[p][0]))
        base.append((f"{skill}/LICENSE", license_bytes, "100644"))
        entry = {"skill": skill, "plugin": info["plugin"], "zips": {}}
        for target in ("source", "claude-web"):
            md = render_skill_md(skill_md, target, f"{prefix}SKILL.md")
            ents = [(n, md.encode("utf-8") if n == f"{skill}/SKILL.md" else d, m) for n, d, m in base]
            name = f"{skill}.zip" if target == "source" else f"{skill}-{target}.zip"
            entry["zips"][target] = {"file": name, "sha256": write_zip(out / name, ents)}
        bundle += [(f"{info['plugin']}/{n}", d, m) for n, d, m in base if n != f"{skill}/LICENSE"]
        manifest["skills"].append(entry)
    bundle.append(("LICENSE", license_bytes, "100644"))
    bname = f"flawpilot-agent-toolkit-{version}.zip"
    manifest["bundle"] = {"file": bname, "sha256": write_zip(out / bname, bundle)}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main(argv: list[str]) -> int:
    ref, out, rest = "HEAD", None, []
    it = iter(argv)
    for a in it:
        if a == "--ref":
            ref = next(it)
        elif a == "--out":
            out = Path(next(it))
        else:
            rest.append(a)
    root = Path(rest[0] if rest else ".")
    try:
        m = build(root, out or root / "dist", ref)
    except (PackageError, subprocess.CalledProcessError) as e:
        print(f"ERROR {getattr(e, 'stderr', b'').decode().strip() if isinstance(e, subprocess.CalledProcessError) else e}")
        return 1
    print(f"Built {len(m['skills'])} skills x 2 targets + {m['bundle']['file']} (version {m['version']})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
