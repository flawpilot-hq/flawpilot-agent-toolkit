---
name: url-scan
description: Run a FlawPilot URL scan and summarize findings. Use when the user asks to scan a website.
license: Apache-2.0
---

# URL scan

## When to use

The user wants a scan of a public URL.

## When NOT to use

The user wants a repository scan; use the code scan skill instead.

## Steps

1. Call `list_projects`, then `trigger_scan`, then poll `get_scan_status`.

See [the reference](references/bands.md).
