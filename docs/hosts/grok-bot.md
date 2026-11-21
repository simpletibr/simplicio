# Simplicio with Grok Bot

Grok Bot is xAI's cloud app. Its always-on agents, which xAI calls AI teammates, each have their own cloud computer. It runs on macOS, Windows and iOS. It is in beta and closed, and it is sold through SuperGrok or Cursor plans.

Grok Bot reaches only remote MCP servers, so it cannot reach the stdio server or the loopback address of your machine. The basis for this is a reply by Cursor staff in a Cursor forum thread, dated 2026-08-13. It says Grok Bot "does not attach MCP servers that run on your own machine, whether that's stdio or something listening on localhost". That reply is not an xAI document.

Needs a Simplicio Runtime that lists `grok-bot` in `simplicio integrate list`.

## What Simplicio does

It writes nothing and starts no tunnel. `simplicio integrations routes grok-bot` prints the documented way and what is not verified. `simplicio integrate install --host grok-bot` writes nothing and names that command.

## The documented way

The route text calls this the documented way, but the only setup source for Grok Bot is a third-party guide. Grok Bot takes remote HTTP and SSE servers and catalog connectors. For Simplicio that means a public HTTPS address for the Simplicio HTTP server, from a tunnel or reverse proxy that you run. The Runtime starts neither. The study names no tunnel for Grok Bot and does not say how to get such an address.

How the product takes a server, per the study. The source is a third-party Composio guide dated 2026-09-03, not an xAI document:

- Add the server in the Plugins marketplace (Settings > Plugins > Yours), or ask the bot in chat to add a custom MCP server at its https address.
- Keys are stored as header or environment values on the server entry.
- The entry is account-wide. A team admin can keep an MCP allowlist.
- A stdio command would run on the bot's cloud computer, not on your laptop. The Simplicio binary on your machine would not be used.
- There is no configuration file.

## Risk

Warning: a tunnel gives the vendor's agent the same tools on this machine as a local agent has. Nothing here was tested.

## Related

The Grok Build command-line agent is a different product, with harness `grok`. For it, use `simplicio integrate install --host grok`.

## Not verified

Every item below is UNVERIFIED.
None of this was run against the real product.

- Setup steps. The only source is a third-party guide, and the xAI documentation for Grok Bot was not read.
- Whether any public address is needed, and how to create one.
- The approval model, timeouts, result caps, tool-name form and client name. The study gives none of them for this product.
- Tool-name prefix, hooks, rules, skill folders, footprint and executable.
- The 1.0 date, 2026-11-02, taken from a search result.

## Sources

"The study" is the Simplicio Runtime's bot harness study of 2026-11-21. It read the vendor
documentation and source named below and ran none of these products.

- https://x.ai/news/introducing-grok-bot (announcement, 2026-08-11)
- https://x.ai/news?d=20261015 (search result; source of the 1.0 date)
- https://x.ai/bot (download page; not opened)
- https://forum.cursor.com/t/does-grok-bot-support-local-mcp-e-g-workflowy/168182 (Cursor forum reply by Cursor staff)
- https://composio.dev/blog/how-to-add-mcp-servers-to-grok-bot (third party)
- https://composio.dev/toolkits/composio/framework/grok-bot.md (third party)
