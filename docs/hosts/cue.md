# Simplicio with Cue by Manus

Cue, by Manus, is a standalone app for personal agents. It runs on web, desktop and mobile. Manus makes it (Butterfly Effect Pte. Ltd.). Each agent has its own email address, phone number, wallet and computer, all in the cloud. Cue describes itself as "built on the same infrastructure as Manus". It is in early access with an invitation code, and it is closed source. The study takes Cue by Manus as the likely product.

Cue reaches only remote servers, so it cannot reach the stdio server or the loopback address of your machine. The study reads the Manus docs as saying a custom server must be accessible over HTTPS, so a localhost address would need a tunnel. That is the study's inference, not a verified fact.

Needs a Simplicio Runtime that lists `cue` in `simplicio integrate list`.

## What Simplicio does

It writes nothing and starts no tunnel. `simplicio integrations routes cue` prints the documented way and what is not verified. `simplicio integrate install --host cue` writes nothing and names that command.

## The documented way

No documented way for Cue was found. Third-party pages say Cue has no connector documentation of its own: adaptlypost.com (as of 2026-09-29) and omentir.com. A catalog site, rankagents.app, says Cue supports MCP. The study calls that weak.

The Manus pages describe custom MCP servers for Manus. They are not confirmed for Cue:

- Settings > Integrations > Custom MCP Servers > Add Server. The fields are a name, an HTTPS URL, and auth ("API key, Bearer token, or other credentials").
- Connectors: choose Create, then Add MCP by URL. A command-based server or an existing JSON configuration goes through Custom MCP or Import MCP by JSON.
- Skills: a Manus Skill is a folder with a SKILL.md file. A help article, quoted by rankagents.app and not read directly by the study, says skills are configured separately in Cue.

For Simplicio, that means a public HTTPS address for the Simplicio HTTP server, from a tunnel or reverse proxy that you run. The Runtime starts neither. The study names no tunnel for Manus or Cue. The study also names a Manus API or custom API connector (a secret plus a note) as an alternative route.

## Risk

Warning: a tunnel gives the vendor's agent the same tools on this machine as a local agent has. The study finds no documentation of how Cue approves connector use. Nothing here was tested.

## Not verified

Every item below is UNVERIFIED.
None of this was run against the real product.

- All MCP points for Cue: transports, config, CLI, tool-name prefix, timeouts, client name, connector approval, hooks and AGENTS.md.
- Whether Cue exposes the Manus Custom MCP screen.
- Where a command-based Custom MCP would run. The study presumes Manus's cloud.
- Whether a Cue skill can run a local command.
- The text of the skills help article.
- Cue's footprint on your machine. A Cue desktop app is named, but its executable name is not verified.

## Sources

"The study" is the Simplicio Runtime's bot harness study of 2026-11-21. It read the vendor
documentation and source named below and ran none of these products.

- https://cue.im
- https://play.google.com/store/apps/details?id=ai.manus.agents
- https://help.manus.im/en/articles/17190150-what-is-new-in-manus-2-0
- https://manus.im/blog/introducing-manus-2-0
- https://adaptlypost.com/blog/manus-cue-connector-social-media-posting (third party)
- https://omentir.com/integrations/manus-cue (third party)
- https://rankagents.app/agents/cue (third party; weak)
- https://manus.im/docs/integrations/custom-mcp
- https://manus.im/features/connectors
- https://www.manus.im/docs/features/skills
- https://help.manus.im/en/articles/14753565-how-to-share-and-use-skills-in-manus (quoted by rankagents.app; not read directly)
