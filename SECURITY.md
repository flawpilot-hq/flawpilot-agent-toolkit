# Security Policy

Skills in this repo run inside AI assistants with access to users' code, so a malicious or careless skill is a real risk. We take reports seriously.

## Report a problem

Report privately through GitHub: the repository's **Security** tab, then **Report a vulnerability** (private vulnerability reporting). Do not open a public issue.

Please include the skill name, what it does wrong, and how to reproduce it. Do not post details publicly until we have replied.

Response target: we acknowledge within 5 working days and aim to fix or remove a confirmed unsafe skill within 14 days.

## Scope

- A skill that exfiltrates data, runs remote code, or asks the assistant to bypass its safety rules.
- A skill whose advice would introduce a vulnerability.
- Secrets committed to the repo.

Not in scope: vulnerabilities in the FlawPilot product itself. Report those through FlawPilot's own channels.

## Repo rules

- Skills may not fetch and execute remote code or contact hosts other than documented FlawPilot endpoints.
- CI scans every pull request for secrets and unsafe skill content.
- Pull requests from forks never receive repository secrets.
