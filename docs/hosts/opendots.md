# Simplicio with OpenDots

OpenDots is an open-source alternative to OpenAI dots. CopilotKit makes it. It is an MIT-licensed, TypeScript project in alpha, and you run it as a self-hosted web app. It has specialist agents called Dots, Spaces and pages, computers through OpenBot, Slack and calls. Conversations need a CopilotKit Intelligence key. OpenDots takes an MCP server by its address, in its own screen.

Needs a Simplicio Runtime that lists `opendots` in `simplicio integrate list`.

## What Simplicio does

Simplicio writes nothing for OpenDots. `simplicio integrations routes opendots` prints the endpoint, the token file and the product's own step. `simplicio integrate install --host opendots` writes nothing and answers `nothing_written`, naming the route command. `simplicio integrate verify --host opendots` answers `not_verifiable`, because the Runtime cannot see a connection made in OpenDots' own screen.

## Steps

1. Start the Simplicio HTTP server on this machine: `simplicio serve --http`. The port is 8787 by default. `--port N` or `SIMPLICIO_HTTP_PORT` change it.
2. The loopback endpoint is `http://127.0.0.1:8787/mcp` (default port). The study reads the OpenDots documentation as saying local addresses work "on the same machine", so keep the server and OpenDots on one host. This was not verified here.
3. The bearer token is in the token file. `simplicio integrations routes opendots` prints its path. The server writes a new token each time it starts, so paste the new token again after a restart.
4. In OpenDots, open the Dot settings ("Edit specialist"), then Connections. Give the connection a name of at most 40 characters. Paste `http://127.0.0.1:8787/mcp` as the Streamable HTTP endpoint. Paste the contents of the token file as the bearer token. Then click Connect. A Refresh button re-lists the tools.

OpenDots takes local addresses and a bearer token only. OAuth-only servers are not supported yet, and OpenDots has no stdio.

OpenDots has no config file and no CLI. It keeps its data in SQLite and stores the token on its server.

## What to expect

- Connections: each connection belongs to one Dot.
- Approval: a tool marked `readOnlyHint` runs without asking. Other tools are "Ask first". They show an approval card, "Approve & run". Approvals work in the web app only. Slack and scheduled runs ask you to go to the web. Each tool can be turned on or off. An approval expires after 1 hour.
- Read-only hints: 8 of Simplicio's 22 tools carry `readOnlyHint`, and 14 carry none. The study names `simplicio_edit` and `simplicio_codegen` as tools that ask first. This count comes from a stand-in client.
- New connection for each call: OpenDots opens a new MCP session for each call and closes it afterwards. Nothing kept in an MCP session survives between calls.
- Result size: OpenDots cuts results at 20,000 characters. On a 17-file test folder, with a stand-in client, Simplicio replies were 7,452 characters at most (single samples). A large tree was not run.
- Time-out: the transport has a 60,000 ms time-out. The study does not say whether it covers connecting, the call, or both.
- Tool names: the model sees `<connection name>__<tool name>`. Each part is a lowercase slug. The connection name is cut to 20 characters and the tool name to 40. Slugs use only `a-z`, `0-9`, `_` and `-`. The separator is a double underscore.
- Limits: at most 100 tools. A tool with a schema above 16,000 bytes is dropped. With a stand-in client, Simplicio's 22 tools had a largest schema of 1,529 characters.
- Not supported: stdio (so no command, arguments or environment variables), OAuth-only servers, and credentials in the URL. Only http and https addresses work.

## Not verified

Every item below is UNVERIFIED.
Nothing was run against the real OpenDots. The flow was measured only with a stand-in client: the official TypeScript MCP client, used the way OpenDots uses it.

- Whether the copy of the OpenDots docs and source read on 2026-11-21 matches the current main branch. The last push seen was 2026-10-12, on a mirror.
- Whether the 60,000 ms time-out covers connecting, the call, or both.
- Whether Simplicio's tool list fits the 100-tool and 16,000-byte limits, and whether its results fit 20,000 characters, in OpenDots itself. A large tree was not run.
- Loopback reachability when OpenDots and the server run on the same host.
- Hooks, AGENTS.md and a plugin marketplace: not seen.

## Sources

"The study" is the Simplicio Runtime's bot harness study of 2026-11-21. It read the vendor
documentation and source named below and ran none of these products.

- https://github.com/CopilotKit/OpenDots
- https://www.copilotkit.ai/opendots
- https://github.com/CopilotKit/OpenDots/blob/main/docs/CONNECTIONS.md
- https://github.com/CopilotKit/OpenDots/blob/main/src/server/connections.ts
