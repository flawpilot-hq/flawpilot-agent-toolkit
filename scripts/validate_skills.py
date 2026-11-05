#!/usr/bin/env python3
"""Validate the marketplace, plugins and skills in this repo.

Usage: python3 scripts/validate_skills.py [--strict] [ROOT]

Errors exit 1. Warnings exit 0 unless --strict. Needs PyYAML.
Rules follow the Claude Code plugin docs, the agentskills.io specification, and CONTRIBUTING.md.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME = 64
MAX_DESC = 1024
MAX_COMPAT = 500
MAX_BODY_LINES = 500
KNOWN_FRONTMATTER = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
RESERVED_PREFIXES = ("claude-", "anthropic-", "anthropics-", "cc-plugin-")
RESERVED_NAMES = {"claude", "anthropic", "anthropics", "claude-code", "claude-mods"}
ALLOWED_MCP_HOSTS = {"mcp.flawpilot.com"}

HOME_PATH_RE = re.compile(r"(/home/[A-Za-z0-9._-]+|/Users/[A-Za-z0-9._-]+|[A-Za-z]:\\Users\\)")
REMOTE_EXEC_RES = [
    re.compile(r"(curl|wget)\b[^\n|]*\|\s*(sudo\s+)?(ba|z|da)?sh\b"),
    re.compile(r"\b(iex|Invoke-Expression)\b.*\b(iwr|Invoke-WebRequest|irm|DownloadString)\b", re.I),
    re.compile(r"\bbase64\s+(-d|--decode)\b[^\n|]*\|\s*(ba|z|da)?sh\b"),
]
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$", re.M)
MCP_TOOL_RE = re.compile(r"\b((?:trigger|get|list|start)_[a-z][a-z0-9_]*)\b")
URL_RE = re.compile(r"\bhttp://[^\s)>\"'`]+")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: Path | str, msg: str) -> None:
        self.errors.append(f"ERROR   {where}: {msg}")

    def warn(self, where: Path | str, msg: str) -> None:
        self.warnings.append(f"WARNING {where}: {msg}")


def load_json(path: Path, rep: Report) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        rep.error(path, "file is missing")
        return None
    except json.JSONDecodeError as e:
        rep.error(path, f"invalid JSON: {e}")
        return None
    if not isinstance(data, dict):
        rep.error(path, "top level must be an object")
        return None
    return data


def check_plugin_name(where: Path, name: object, rep: Report) -> None:
    if not isinstance(name, str) or not NAME_RE.match(name):
        rep.error(where, f"plugin name {name!r} must be kebab-case")
        return
    if name in RESERVED_NAMES or name.startswith(RESERVED_PREFIXES):
        rep.error(where, f"plugin name {name!r} is reserved for Anthropic")


def split_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    if not text.startswith("---"):
        return None, text, "SKILL.md must start with YAML frontmatter (---)"
    parts = text.split("\n---", 1)
    if len(parts) != 2:
        return None, text, "frontmatter is not closed with ---"
    head = parts[0][3:]
    body = parts[1].split("\n", 1)[1] if "\n" in parts[1] else ""
    try:
        data = yaml.safe_load(head)
    except yaml.YAMLError as e:
        return None, body, f"frontmatter is not valid YAML: {e}"
    if not isinstance(data, dict):
        return None, body, "frontmatter must be a YAML mapping"
    return data, body, None


def check_skill(skill_dir: Path, plugin: str, tool_names: set[str] | None, root: Path, rep: Report) -> None:
    md = skill_dir / "SKILL.md"
    rel = md.relative_to(root)
    if not md.is_file():
        rep.error(skill_dir.relative_to(root), "skill folder has no SKILL.md")
        return
    text = md.read_text(encoding="utf-8")
    fm, body, err = split_frontmatter(text)
    if err or fm is None:
        rep.error(rel, err or "bad frontmatter")
        return

    name = fm.get("name")
    if not isinstance(name, str) or not name:
        rep.error(rel, "frontmatter `name` is required")
    else:
        if len(name) > MAX_NAME:
            rep.error(rel, f"name is {len(name)} characters, max {MAX_NAME}")
        if not NAME_RE.match(name):
            rep.error(rel, f"name {name!r} must be lowercase letters, digits and single hyphens, not starting or ending with a hyphen")
        if name != skill_dir.name:
            rep.error(rel, f"name {name!r} must match the folder name {skill_dir.name!r}")
        if name.startswith(plugin + "-") or name == plugin:
            rep.error(rel, f"name {name!r} repeats the plugin name; skills are already namespaced as /{plugin}:<skill>")

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        rep.error(rel, "frontmatter `description` is required and must be non-empty")
    elif len(desc) > MAX_DESC:
        rep.error(rel, f"description is {len(desc)} characters, max {MAX_DESC}")

    compat = fm.get("compatibility")
    if compat is not None and (not isinstance(compat, str) or not 1 <= len(compat) <= MAX_COMPAT):
        rep.error(rel, f"compatibility must be a string of 1-{MAX_COMPAT} characters")
    meta = fm.get("metadata")
    if meta is not None and not (isinstance(meta, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in meta.items())):
        rep.error(rel, "metadata must be a map of string keys to string values")
    for key in fm:
        if key not in KNOWN_FRONTMATTER:
            rep.warn(rel, f"unknown frontmatter field {key!r}")

    lines = text.count("\n") + 1
    if lines > MAX_BODY_LINES:
        rep.error(rel, f"SKILL.md has {lines} lines, max {MAX_BODY_LINES}; move detail into references/")

    headings = [h.strip().lower() for h in HEADING_RE.findall(body)]
    if not any(h.startswith("when to use") for h in headings):
        rep.error(rel, 'missing a "When to use" heading')
    if not any(h.startswith("when not to use") for h in headings):
        rep.error(rel, 'missing a "When NOT to use" heading')

    scan_files = [p for p in skill_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".txt", ".sh", ".py", ".js", ".json", ".yml", ".yaml"}]
    for f in scan_files:
        frel = f.relative_to(root)
        try:
            ftext = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            rep.error(frel, "file is not valid UTF-8 text")
            continue
        if HOME_PATH_RE.search(ftext):
            rep.error(frel, "contains a hardcoded user home path")
        for rx in REMOTE_EXEC_RES:
            if rx.search(ftext):
                rep.error(frel, "downloads and executes remote code, which skills must not do")
        for m in URL_RE.finditer(ftext):
            host = urlparse(m.group(0)).hostname or ""
            if host not in {"localhost", "127.0.0.1", "::1"}:
                rep.error(frel, f"plain http:// URL to {host!r}; use https://")

    for target in MD_LINK_RE.findall(body):
        t = target.split("#", 1)[0]
        if not t or re.match(r"^[a-z][a-z0-9+.-]*:", t, re.I):
            continue
        if not (skill_dir / t).resolve().is_relative_to(skill_dir.resolve()):
            rep.error(rel, f"link {target!r} points outside the skill folder")
        elif not (skill_dir / t).exists():
            rep.error(rel, f"broken file reference {target!r}")

    if tool_names is not None:
        for tool in sorted(set(MCP_TOOL_RE.findall(text))):
            if tool not in tool_names:
                rep.error(rel, f"mentions tool {tool!r} which is not in plugins/{plugin}/tools.json")


def load_tool_names(plugin_dir: Path, rep: Report, root: Path, release: bool = False) -> set[str] | None:
    path = plugin_dir / "tools.json"
    if not path.exists():
        return None
    data = load_json(path, rep)
    if data is None:
        return set()
    names: set[str] = set()
    tools = data.get("tools", {})
    groups = tools.values() if isinstance(tools, dict) else [tools]
    for g in groups:
        if isinstance(g, list):
            names.update(x for x in g if isinstance(x, str))
    aliases = data.get("aliases", [])
    if isinstance(aliases, list):
        names.update(x for x in aliases if isinstance(x, str))
    if not names:
        rep.error(path.relative_to(root), "tools.json lists no tool names")
    if release and data.get("verified") is not True:
        rep.error(path.relative_to(root), "tools.json is not `verified: true`; verify against a live tools/list before a release")
    return names


def check_mcp(plugin_dir: Path, root: Path, rep: Report) -> None:
    path = plugin_dir / ".mcp.json"
    if not path.exists():
        return
    rel = path.relative_to(root)
    data = load_json(path, rep)
    if data is None:
        return
    servers = data.get("mcpServers", {})
    if not isinstance(servers, dict) or not servers:
        rep.error(rel, "mcpServers must be a non-empty object")
        return
    for sname, cfg in servers.items():
        if not isinstance(cfg, dict):
            rep.error(rel, f"server {sname!r} must be an object")
            continue
        if "command" in cfg:
            rep.error(rel, f"server {sname!r} runs a local command; only remote https servers are allowed")
        url = cfg.get("url")
        parsed = urlparse(url) if isinstance(url, str) else None
        if not parsed or parsed.scheme != "https" or parsed.hostname not in ALLOWED_MCP_HOSTS:
            rep.error(rel, f"server {sname!r} url must be https on one of {sorted(ALLOWED_MCP_HOSTS)}")
        for hk, hv in (cfg.get("headers") or {}).items():
            if not (isinstance(hv, str) and re.search(r"\$\{[^}]+\}", hv)):
                rep.error(rel, f"header {hk!r} has a literal value; never commit credentials (use ${{...}} or OAuth)")


def validate(root: Path, release: bool = False) -> Report:
    rep = Report()
    root = root.resolve()  # macOS tmp dirs are symlinks (/var -> /private/var)
    mkt_path = root / ".claude-plugin" / "marketplace.json"
    mkt = load_json(mkt_path, rep)
    if mkt is None:
        return rep
    mrel = mkt_path.relative_to(root)
    if not isinstance(mkt.get("name"), str) or not NAME_RE.match(mkt["name"]):
        rep.error(mrel, "marketplace `name` is required and must be kebab-case")
    owner = mkt.get("owner")
    if not (isinstance(owner, dict) and isinstance(owner.get("name"), str) and owner["name"]):
        rep.error(mrel, "`owner.name` is required")
    entries = mkt.get("plugins")
    if not isinstance(entries, list) or not entries:
        rep.error(mrel, "`plugins` must be a non-empty array")
        return rep

    listed: set[str] = set()
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").exists() else ""
    for entry in entries:
        ename = entry.get("name") if isinstance(entry, dict) else None
        source = entry.get("source") if isinstance(entry, dict) else None
        if not isinstance(ename, str) or not isinstance(source, str):
            rep.error(mrel, "each plugin entry needs a string `name` and `source`")
            continue
        check_plugin_name(mrel, ename, rep)
        if ename in listed:
            rep.error(mrel, f"plugin {ename!r} is listed twice")
        listed.add(ename)
        if not source.startswith("./") or ".." in Path(source).parts:
            rep.error(mrel, f"source {source!r} must start with ./ and not contain ..")
            continue
        pdir = (root / source).resolve()
        if not pdir.is_relative_to(root.resolve()) or not pdir.is_dir():
            rep.error(mrel, f"source {source!r} is not a folder inside the repo")
            continue
        pj = pdir / ".claude-plugin" / "plugin.json"
        manifest = load_json(pj, rep)
        if manifest is None:
            continue
        pjrel = pj.relative_to(root)
        if manifest.get("name") != ename:
            rep.error(pjrel, f"manifest name {manifest.get('name')!r} must equal the marketplace entry name {ename!r}")
        if not isinstance(manifest.get("version"), str) or not manifest["version"]:
            rep.error(pjrel, "`version` is required here (users stay on the pinned version until it changes)")
        if not manifest.get("license"):
            rep.warn(pjrel, "no `license` set")
        if ename not in readme:
            rep.warn("README.md", f"plugin {ename!r} is not mentioned in the README")

        tool_names = load_tool_names(pdir, rep, root, release)
        check_mcp(pdir, root, rep)
        skills_dir = pdir / "skills"
        if skills_dir.is_dir():
            for sd in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
                check_skill(sd, ename, tool_names, root, rep)

    plugins_root = root / "plugins"
    if plugins_root.is_dir():
        for d in sorted(p for p in plugins_root.iterdir() if p.is_dir()):
            if d.name not in listed:
                rep.error(d.relative_to(root), "plugin folder is not listed in marketplace.json")
    return rep


def main(argv: list[str]) -> int:
    strict = "--strict" in argv
    args = [a for a in argv if not a.startswith("--")]
    root = Path(args[0] if args else ".").resolve()
    rep = validate(root, release="--release" in argv)
    for line in rep.errors + rep.warnings:
        print(line)
    failed = bool(rep.errors) or (strict and bool(rep.warnings))
    print(f"\n{len(rep.errors)} error(s), {len(rep.warnings)} warning(s){' [strict]' if strict else ''}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
