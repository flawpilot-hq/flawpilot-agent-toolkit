# Contributing

Thanks for helping. Skills here run inside people's coding assistants, so quality and safety matter more than volume.

## PR checklist for a skill

- [ ] Folder is `plugins/<plugin>/skills/<name>/SKILL.md` and `name` in the frontmatter matches the folder.
- [ ] `name`: lowercase letters, digits and single hyphens, 64 characters or fewer. Do not repeat the plugin name (it is added automatically: `/flawpilot:url-scan`).
- [ ] `description`: 1024 characters or fewer, says what the skill does and when to use it.
- [ ] Has "When to use" and "When NOT to use" sections.
- [ ] `SKILL.md` is under 500 lines; long material is in `references/`.
- [ ] Findings cite evidence (file and line) and say how confident they are.
- [ ] Defensive only: no exploit-writing or attacks on systems the user does not own.
- [ ] Standards are cited by name and version.
- [ ] No scripts that download and run remote code; no network calls except documented FlawPilot endpoints.
- [ ] FlawPilot skills only name MCP tools listed in `plugins/flawpilot/tools.json`.
- [ ] Skill is registered in the plugin and the root README table is updated.
- [ ] `python3 scripts/validate_skills.py --strict .` and `claude plugin validate . --strict` pass (CI runs both).

## Reviews

A maintainer reviews every pull request. Target: first response within 7 days. Issues with no activity for 90 days may be closed.

## Security issues

Do not open a public issue. See `SECURITY.md`.
