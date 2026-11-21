# Simplicio with Dots

Dots is OpenAI's always-on cloud agent inside ChatGPT. Each dot has its own cloud computer and browser. It is closed source. Access depends on the plan: Pro, Business Premium, and Enterprise and Edu (from an admin preview, default-on from 2026-11-18).

Dots reaches only remote MCP servers, so it cannot reach the stdio server or the loopback address of your machine. OpenAI's help article says: "Can I connect to a local MCP server? Not directly. ChatGPT connects to remote MCP servers."

Needs a Simplicio Runtime that lists `dots` in `simplicio integrate list`.

## What Simplicio does

It writes nothing and starts no tunnel. `simplicio integrations routes dots` prints the documented way and what is not verified. `simplicio integrate install --host dots` writes nothing and names that command.

## The documented way

The route uses OpenAI's Secure MCP Tunnel. The tunnel client wraps the stdio command, so no public address is needed. The tunnel ID and an API key come from the OpenAI Platform settings. Run these two commands on the machine that has the Simplicio binary, with `<path to simplicio>` set to its path. The tunnel client starts the stdio command itself:

```bash
tunnel-client init --sample sample_mcp_stdio_local --profile local-stdio --tunnel-id <tunnel_id> --mcp-command "<path to simplicio> serve --mcp --stdio --no-facade-mode"
tunnel-client run --profile local-stdio
```

Then, in ChatGPT on the web:

1. Open Plugins, then `+`, then Add custom MCP server.
2. Enter a name.
3. Set Connection to Tunnel.
4. Choose the auth: OAuth, none or mixed. The study names no bearer-token option.
5. Accept the risk warning, choose Create as a plugin, and install.

A plugin made this way is shared by the dots, ChatGPT and Codex of the account (third-party OpenLore document). Whether a dot can use a plugin made over a Tunnel is UNVERIFIED: the dot pages do not say.

Plan limits (OpenAI help article):

- Full custom MCP support is on Business, Enterprise and Edu. Pro is read and fetch only.
- On Business, only admins and owners create servers.
- The tool list is a snapshot. It stays frozen until an admin republishes it (OpenAI help article; third-party knowman guide).

## Risk

Warning: a tunnel gives the vendor's agent the same tools on this machine as a local agent has. ChatGPT asks before it runs a write tool; the study says that choice comes from the tool's `readOnlyHint` annotation (third-party OpenLore document). Nothing here was tested.

## Not verified

Every item below is UNVERIFIED.
None of this was run against the real product.

- Whether a dot can use a plugin made over a Tunnel. The dot pages do not say.
- Whether every custom plugin is usable by a dot. The sources conflict: a third-party guide (knowman) says OpenAI does not explicitly document custom MCP for dots, while third-party Willow and dopost docs show it working for dots.
- A dot-specific MCP page. None was found.
- Whether the Simplicio bearer token can be used here. The study names no bearer-token option.
- Tool-name prefix, timeouts and client name.
- Hooks and AGENTS.md.

## Sources

"The study" is the Simplicio Runtime's bot harness study of 2026-11-21. It read the vendor
documentation and source named below and ran none of these products.

- https://openai.com/index/introducing-dots/
- https://learn.chatgpt.com/docs/dots
- https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt
- https://developers.openai.com/api/docs/guides/custom-mcp-server
- https://developers.openai.com/plugins/deploy/connect-chatgpt
- https://developers.openai.com/api/docs/guides/secure-mcp-tunnels
- https://github.com/aakarim/OpenLore/blob/main/docs/start/agents/openai-dots.md (third party)
- https://www.knowman.io/guides/chatgpt-dots-knowledge-base (third party)
- https://docs.withwillow.ai/scout/assistants/dots (third party)
- https://dopost.co/docs/api/ai-agents/dots (third party)
- https://mcp.so/blog/chatgpt-mcp-setup (third party; Codex route)
