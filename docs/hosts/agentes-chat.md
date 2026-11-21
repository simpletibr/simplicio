# Simplicio with agentes.chat

The product is agentes.chat, spelled with an e. It is a team chat where people and AI agents work together. It is an alternative to Slack, made by AGENTESCHAT, LLC. It has a paid Cloud plan and a free self-hosted version. It opened as a beta in November 2026. It is a web, desktop and phone workspace, not a command-line tool.

The site agents.chat, spelled without the e, is a different site, not this product. The study found it to be a travel-guide index with no agent features.

Use this route only with a self-hosted agentes.chat. The study infers that the Cloud plan cannot reach an address on your machine, because it is built on URL-based connectors. That inference is not verified.

Needs a Simplicio Runtime that lists `agentes-chat` in `simplicio integrate list`.

## What Simplicio does

Simplicio writes nothing for agentes.chat. `simplicio integrations routes agentes-chat` prints the endpoint, the token file and the product's own step. `simplicio integrate install --host agentes-chat` writes nothing and answers `nothing_written`, naming the route command. `simplicio integrate verify --host agentes-chat` answers `not_verifiable`, because the Runtime cannot see a connection made in the product's own screen.

## Steps

1. Start the Simplicio HTTP server on this machine: `simplicio serve --http`. The port is 8787 by default. `--port N` or `SIMPLICIO_HTTP_PORT` change it.
2. The loopback endpoint is `http://127.0.0.1:8787/mcp` (default port). Use a self-hosted agentes.chat on this same machine. Whether a self-hosted instance reaches this address is UNVERIFIED.
3. The bearer token is in the token file. `simplicio integrations routes agentes-chat` prints its path. The server writes a new token each time it starts, so paste the new token again after a restart. Whether agentes.chat accepts a bearer token is UNVERIFIED.
4. In agentes.chat, open the organization's connectors (Connectors (MCP)). Add a server by URL, with `http://127.0.0.1:8787/mcp` as the URL.
5. Set the access of each agent: read only, read-write, or ask for approval.

## What to expect

- Access: each agent gets read only, read-write, or ask-for-approval access.
- Approvals: merge, deploy and rollback always need a person. The study says sensitive connector actions need approval too.
- Agent computers: agents run commands on a connected computer, where a runner is installed. The study names this as the documented local route. A Simplicio CLI could be given to an agent through a skill (`SKILL.md`) or through a shell on that computer. The study does not say that this works with Simplicio.
- No hooks are documented, and no reading of AGENTS.md is documented.
- The study states no result-size limit, no time-out and no rule for a new session on each call in agentes.chat. The timeouts, the client name and the tool-name prefix are UNVERIFIED.
- This page covers one direction only. agentes.chat is also an MCP server for Claude, Cursor and others, at an address under Settings > AI apps that ends in `/mcp`. That does not connect Simplicio to agentes.chat.

## Not verified

Every item below is UNVERIFIED.
Nothing was run against the real product. The only measurement is a stand-in client that behaves the way
OpenDots does (see the OpenDots page); agentes.chat is not OpenDots, so it says little about this product.

- Connector fields, and whether a stdio server can be attached. The study read URL-based docs only.
- Whether a bearer token is accepted (see Steps).
- Timeouts, client name and tool-name prefix.
- Whether a self-hosted instance reaches the loopback address (an inference).
- Whether the "OpenBot.run" entry of the agentes.chat import list is CopilotKit OpenBot.
- The contents of the self-hosted install script at https://agentes.chat/install (not read).
- Hooks, AGENTS.md and rules: not found in the sources read.

## Sources

"The study" is the Simplicio Runtime's bot harness study of 2026-11-21. It read the vendor
documentation and source named below and ran none of these products.

- https://agentes.chat/docs/import
- https://agentes.chat/docs/ai-apps
- https://agentes.chat/pt/sobre
- http://github.com/agentes-chat/agentes-chat
