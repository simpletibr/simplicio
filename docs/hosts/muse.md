# Simplicio with the Muse app

The Muse app is Meta's personal agent app, launched 2026-09-08. Each user gets a cloud virtual machine; a third-party test describes it as a Debian VM. The app is closed.

The Muse app reaches only remote MCP servers, so it cannot reach the stdio server or the loopback address of your machine. Its agent runs on that cloud VM. A server on your laptop, or on 127.0.0.1, is not reachable from it, according to a third-party test.

No hooks and no AGENTS.md are documented for the app. Its footprint on your machine is none, since the agent runs in the cloud.

Needs a Simplicio Runtime that lists `muse` in `simplicio integrate list`.

## What Simplicio does

It writes nothing and starts no tunnel. `simplicio integrations routes muse` prints the documented way and what is not verified. `simplicio integrate install --host muse` writes nothing and names that command.

## The documented way

The route text gives a public HTTPS address for the Simplicio HTTP server as the way in. It comes from a tunnel or reverse proxy that you run. The Runtime starts neither. The study names no way to create that address.

How the app takes a server, per the study:

- Meta's help page describes Connectors (a curated list in Settings > Connectors) and Custom Connectors. It says you can ask Muse to create a Custom Connector. Muse stores these in its Secure Credentials Store.
- A third-party article (November 2026) says the Muse app has no "add MCP server" setting. It is not a Meta document.
- A third-party test found that Muse can write an MCP client on its VM and save it as a skill. A public streamable HTTP URL worked. A stdio server works only if it can be installed on the VM, with npm or pip.
- The Muse Connector Platform takes a connector for review (functional, security and legal checks): https://platform.muse.ai/

## Risk

Warning: a tunnel gives the vendor's agent the same tools on this machine as a local agent has. Meta's help page says "Meta doesn't review custom connectors", and connectors can be set to read-only, ask or allow in Settings. Nothing here was tested.

## Related

The Muse Code command-line agent is a different product, with harness `muse-code`. For it, use `simplicio integrate install --host muse-code`.

## Not verified

Every item below is UNVERIFIED.
None of this was run against the real product.

- Any official Meta statement that the app supports MCP servers. The only "no setting" statement is third party.
- Whether the third-party test still holds for the current app.
- Whether the Muse VM reaches a public URL today.
- Client name, timeouts and tool-name form.

## Sources

"The study" is the Simplicio Runtime's bot harness study of 2026-11-21. It read the vendor
documentation and source named below and ran none of these products.

- https://www.meta.com/help/artificial-intelligence/1687253048996149/
- https://parallel.ai/articles/meta-muse-custom-integrations (third party)
- https://platform.muse.ai/
