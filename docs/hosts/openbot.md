# Simplicio with OpenBot

OpenBot is a self-hostable AI bot from CopilotKit, under the MIT licence. It calls itself "The open, self-hostable alternative to closed AI bots". It runs on desktop (Mac and Windows, with a Docker backend), web, iOS, Android, Slack and Teams. It takes a remote MCP server by its address, in its own screen.

The identity is a guess. This page takes OpenBot to be CopilotKit OpenBot (open.bot). The study rates that choice MEDIUM, and it is UNVERIFIED.

Needs a Simplicio Runtime that lists `openbot` in `simplicio integrate list`.

## What Simplicio does

Simplicio writes nothing for OpenBot. `simplicio integrations routes openbot` prints the endpoint, the token file and the product's own step. `simplicio integrate install --host openbot` writes nothing and answers `nothing_written`, naming the route command. `simplicio integrate verify --host openbot` answers `not_verifiable`, because the Runtime cannot see a connection made in OpenBot's own screen.

## Steps

1. Start the Simplicio HTTP server on this machine: `simplicio serve --http`. The port is 8787 by default. `--port N` or `SIMPLICIO_HTTP_PORT` change it.
2. The loopback endpoint is `http://127.0.0.1:8787/mcp` (default port).
3. The bearer token is in the token file. `simplicio integrations routes openbot` prints its path. The server writes a new token each time it starts, so paste the new token again after a restart. The study does not say how OpenBot takes a token (see Not verified).
4. On the OpenBot side, set `OPENBOT_ALLOW_LOOPBACK_MCP=1`. Without it, OpenBot takes https addresses only, with no IP literal and no localhost. The variable allows `http://127.0.0.1:<port>`. The docs call it a development override.
5. In OpenBot, open Connections, then Add server. Give `http://127.0.0.1:8787/mcp` as the address.

## What to expect

- Authentication: OpenBot offers OAuth under the MCP auth spec, or a static key. The study does not say how a static key is sent.
- Approval: an admin governs MCP access. Each MCP call checks the grant, then the action policy, then the audit log.
- Tools: custom-server tools are treated as writes unless they are classified as read.
- Team edition: an "Only approved servers" allowlist. Personal edition: no allowlist.
- Addresses: HTTPS only, with no IP literal, no localhost and no internal host. The development override above also allows `[::1]`.
- No stdio: open issue 1685 of the repository says the Add server flow takes remote HTTPS endpoints only. It has no command, args or env fields for stdio servers.
- Configuration: through the UI and an API. There is no user config file, and no CLI `mcp add` was found.
- The study states no result-size limit, no time-out and no rule for a new session on each call in OpenBot. The tool-name prefix, the time-outs and the client name are UNVERIFIED.

## Not verified

Every item below is UNVERIFIED.
Nothing was run against the real product. The only measurement is a stand-in client that behaves the way
OpenDots does (see the OpenDots page); OpenBot is not OpenDots, so it says little about this product.

- The identity of the product (a guess).
- Whether `OpenBot.run` in the agentes.chat import list is this product.
- Whether the development override works in the desktop build, and whether a Docker backend reaches the host's loopback address.
- How a static key or bearer token is entered in the Add server screen, and whether OpenBot accepts the per-session token of the Simplicio server.
- Tool-name prefix, timeouts and client name.
- Hooks, AGENTS.md, `rules/`, footprint and executable name.

## Sources

"The study" is the Simplicio Runtime's bot harness study of 2026-11-21. It read the vendor
documentation and source named below and ran none of these products.

- https://github.com/CopilotKit/OpenBot
- https://www.copilotkit.ai/blog/openbot-whats-new
- https://raw.githubusercontent.com/CopilotKit/OpenBot/main/docs/plugins/mcp-by-url.md
- https://github.com/CopilotKit/OpenBot/issues/1685
- https://github.com/CopilotKit/OpenBot/blob/HEAD/docs/configuration.md
