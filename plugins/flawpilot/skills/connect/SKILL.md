---
name: connect
description: Connect an AI assistant to the FlawPilot MCP server, or fix a broken connection. Use when FlawPilot tools are missing, authentication fails or loops, the user asks how to set up FlawPilot in Claude, ChatGPT, Gemini, Cursor or VS Code, or asks about API keys and revoking access.
---

# Connect to FlawPilot

FlawPilot runs a remote MCP server. Nothing is installed locally.

- Server URL: `https://mcp.flawpilot.com/mcp` (Streamable HTTP)
- Preferred auth: OAuth in the browser. No key to copy.
- Fallback auth: a FlawPilot API key sent as `Authorization: Bearer <key>`.

## When to use

- No FlawPilot tools appear (`list_projects`, `trigger_scan` and the rest).
- Sign-in fails, loops, or the browser never opens.
- The user wants setup steps for a specific client.
- The user asks how to disconnect or revoke access.

## When NOT to use

- Tools are connected and a scan fails. Use the `errors` skill.
- The user wants to run a scan. Use `url-scan`, `site-health` or `code-scan`.

## Check the connection first

Call `list_projects`. If it returns projects, the connection works and nothing else is needed. An empty list means connected but no projects yet; tell the user to create one in the dashboard.

If the tool does not exist or returns an auth error, continue below.

## Setup per client

| Client | Steps |
|---|---|
| Claude Code | `claude mcp add flawpilot --transport http https://mcp.flawpilot.com/mcp` with no header. A browser opens to approve. This plugin already ships that config, so installing the plugin starts the same approval. |
| Claude Desktop, claude.ai | Settings, Connectors, Directory, search "flawpilot", Connect. Approve the workspace in the browser. |
| ChatGPT | Follow the ChatGPT page at https://docs.flawpilot.com/mcp-connect/chatgpt, since ChatGPT menus change often. Approve the workspace. Make sure the FlawPilot chip is active on the message, or ChatGPT answers from its own knowledge. |
| Gemini | Follow https://docs.flawpilot.com/mcp-connect/gemini, since Gemini menus change often. You add the server URL as a custom app and approve the workspace. "Not reviewed by Google" is expected for custom apps. Check the URL reads flawpilot.com. |
| VS Code, Cursor, others | Add a remote HTTP server with the URL above. Use OAuth if the client supports it; otherwise add a Bearer header (see below). |

After connecting, start a new conversation. Assistants load tools when a chat begins, so an open chat will not see them.

## API key path

Only when the client cannot do OAuth.

1. In FlawPilot: Settings, API keys, Generate key. This needs the Owner or Admin role.
2. The key is shown once. FlawPilot stores only a hash.
3. Put the key in the client's secret or input store. Never write it into a file that is committed, and never paste it into chat.

Tell the user that an API key authenticates as the whole workspace.

## Things to tell the user

- OAuth still creates an ordinary API key named after the client. It appears in Settings, API keys.
- Disconnecting in the client does **not** revoke that key. To fully remove access, revoke the key in Settings, API keys.
- Keys do not expire on their own. Use one key per integration.
- If a brand-new account cannot connect, say so and suggest checking again later or contacting FlawPilot support.

## Troubleshooting

| Problem | Fix |
|---|---|
| Tools do not show up | Start a new conversation. |
| Authentication loops | Sign in to FlawPilot in the same browser, check the pop-up blocker. |
| Gemini tool list empty | Remove the connection and add it again. |
| ChatGPT ignores FlawPilot | Check the chip is active, or mention FlawPilot by name. |
| Wrong workspace | The connection is scoped to the workspace chosen at approval. Disconnect and approve again with the right one. |

Do not ask the user to paste a key into the conversation. If a key was pasted, tell them to revoke it and generate a new one.
