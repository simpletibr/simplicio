// OpenCode host harness (#450).
//
// Simulates the real host path without an LLM or Playwright:
//   1. loads the managed plugin the way OpenCode V2 does (default export with
//      `id` + `setup`), captures the hook the plugin registers, and proves
//      native `read`/`write`/`edit`/`shell` are rejected while `simplicio_*`
//      and third-party MCP tools pass through;
//   2. for the acceptance scenario, delivers a native `write` for index.html
//      (rejected, no file), then performs the governed `simplicio_edit` call
//      over a real MCP stdio session and asserts the effect receipt carries a
//      write_set for index.html.
//
// Usage:
//   node opencode_host_harness.mjs contract --plugin <dir>
//   node opencode_host_harness.mjs html --plugin <dir> --repo <dir> --binary <simplicio>

import { spawn } from "node:child_process";
import path from "node:path";
import { pathToFileURL } from "node:url";

const NATIVE = ["read", "write", "edit", "shell"];
const PASSTHROUGH = ["simplicio_edit", "simplicio_file", "simplicio_exec", "third_party_tool", "mcp__github__issue"];

function parseArgs(argv) {
  const [mode, ...rest] = argv;
  const options = { mode };
  for (let index = 0; index < rest.length; index += 2) {
    options[rest[index].replace(/^--/, "")] = rest[index + 1];
  }
  return options;
}

async function loadPlugin(directory) {
  const entry = path.join(directory, "index.js");
  const module = await import(pathToFileURL(entry).href);
  const plugin = module.default;
  if (!plugin || typeof plugin !== "object") throw new Error("plugin default export must be an object");
  if (plugin.id !== "simplicio") throw new Error(`unexpected plugin id: ${plugin.id}`);
  if (typeof plugin.setup !== "function") throw new Error("plugin must expose a V2 setup function");

  let hook = null;
  const ctx = {
    tool: {
      hook: async (name, callback) => {
        hook = { name, callback };
      },
    },
  };
  await plugin.setup(ctx);
  if (!hook || hook.name !== "execute.before") throw new Error("plugin did not register execute.before");

  const v1Hooks = typeof plugin.server === "function" ? await plugin.server() : {};
  const v1 = v1Hooks["tool.execute.before"];

  async function blocked(callback, tool) {
    try {
      await callback({ tool });
      return null;
    } catch (error) {
      return error instanceof Error ? error.message : String(error);
    }
  }

  const nativeResults = {};
  for (const tool of NATIVE) nativeResults[tool] = await blocked(hook.callback, tool);
  const passthroughResults = {};
  for (const tool of PASSTHROUGH) passthroughResults[tool] = await blocked(hook.callback, tool);
  const v1Results = {};
  if (typeof v1 === "function") for (const tool of NATIVE) v1Results[tool] = await blocked(v1, tool);

  return { entry, plugin, hook, nativeResults, passthroughResults, v1Results };
}

class McpClient {
  constructor(binary, repo) {
    this.sequence = 0;
    this.pending = new Map();
    this.buffer = "";
    this.child = spawn(binary, ["serve", "--mcp", "--stdio", "--no-facade-mode"], {
      cwd: repo,
      env: { ...process.env, SIMPLICIO_MCP_PROFILE: "full", SIMPLICIO_RUNTIME_MODE: "full" },
      stdio: ["pipe", "pipe", "pipe"],
    });
    this.child.stdout.setEncoding("utf8");
    this.child.stdout.on("data", (chunk) => this.consume(chunk));
    this.child.stderr.setEncoding("utf8");
    this.stderr = "";
    this.child.stderr.on("data", (chunk) => (this.stderr += chunk));
  }

  consume(chunk) {
    this.buffer += chunk;
    let index;
    while ((index = this.buffer.indexOf("\n")) >= 0) {
      const line = this.buffer.slice(0, index).trim();
      this.buffer = this.buffer.slice(index + 1);
      if (!line) continue;
      let message;
      try {
        message = JSON.parse(line);
      } catch {
        continue;
      }
      const waiter = this.pending.get(message.id);
      if (waiter) {
        this.pending.delete(message.id);
        waiter(message);
      }
    }
  }

  request(method, params, timeoutMs = 20000) {
    const id = ++this.sequence;
    const payload = { jsonrpc: "2.0", id, method, params };
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`MCP timeout: ${method}`));
      }, timeoutMs);
      this.pending.set(id, (message) => {
        clearTimeout(timer);
        if (message.error) reject(new Error(message.error.message || JSON.stringify(message.error)));
        else resolve(message.result);
      });
      this.child.stdin.write(JSON.stringify(payload) + "\n");
    });
  }

  notify(method, params) {
    this.child.stdin.write(JSON.stringify({ jsonrpc: "2.0", method, params }) + "\n");
  }

  close() {
    this.child.kill();
  }
}

function textPayload(result) {
  const text = result?.content?.find((item) => item.type === "text")?.text;
  if (!text) throw new Error("MCP result had no text content");
  return JSON.parse(text);
}

async function htmlAcceptance({ plugin, repo, binary }) {
  const first = await (async () => {
    try {
      await plugin.hook.callback({ tool: "write" });
      return null;
    } catch (error) {
      return error.message;
    }
  })();
  const file = path.join(repo, "index.html");
  const { existsSync, readFileSync } = await import("node:fs");

  const client = new McpClient(binary, repo);
  let receipt;
  try {
    await client.request("initialize", {
      protocolVersion: "2025-06-18",
      capabilities: {},
      clientInfo: { name: "opencode-host-harness", version: "1.0.0" },
    });
    client.notify("notifications/initialized", {});
    const content = "<!doctype html>\n<html><head><title>Simplicio</title></head><body><h1>ok</h1></body></html>\n";
    const result = await client.request("tools/call", {
      name: "simplicio_edit",
      arguments: { repo, file: "index.html", content, apply: true },
    });
    if (result?.isError) throw new Error("governed simplicio_edit failed: " + JSON.stringify(result));
    receipt = textPayload(result);
  } finally {
    client.close();
  }

  const writeSet = receipt?.governed_artifact_receipt?.write_set ?? receipt?.write_set ?? [];
  const secondAttempt = await (async () => {
    try {
      await plugin.hook.callback({ tool: "write" });
      return null;
    } catch (error) {
      return error.message;
    }
  })();

  return {
    native_write_blocked: Boolean(first),
    native_write_error: first,
    receipt_schema: receipt?.schema ?? null,
    write_set: writeSet,
    file_created_by_governed_edit: existsSync(file),
    file_bytes: existsSync(file) ? readFileSync(file).length : 0,
    second_native_write_blocked: Boolean(secondAttempt),
  };
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const loaded = await loadPlugin(options.plugin);
  const contract = {
    schema: "simplicio.opencode-host-harness/v1",
    ok:
      NATIVE.every((tool) => Boolean(loaded.nativeResults[tool])) &&
      PASSTHROUGH.every((tool) => loaded.passthroughResults[tool] === null) &&
      NATIVE.every((tool) => Boolean(loaded.v1Results[tool])),
    plugin: { id: loaded.plugin.id, entry: loaded.entry, hook: loaded.hook.name },
    blocked: loaded.nativeResults,
    passthrough: loaded.passthroughResults,
    v1_blocked: loaded.v1Results,
  };
  if (options.mode === "contract") {
    console.log(JSON.stringify(contract));
    process.exit(contract.ok ? 0 : 1);
  }
  if (options.mode !== "html") throw new Error(`unknown mode: ${options.mode}`);

  const acceptance = await htmlAcceptance({
    plugin: loaded,
    repo: options.repo,
    binary: options.binary,
  });
  const ok =
    contract.ok &&
    acceptance.native_write_blocked &&
    acceptance.second_native_write_blocked &&
    acceptance.file_created_by_governed_edit &&
    acceptance.file_bytes > 0 &&
    acceptance.receipt_schema === "simplicio.effect-receipt/v1" &&
    acceptance.write_set.includes("index.html");
  console.log(JSON.stringify({ ...contract, ok, acceptance }));
  process.exit(ok ? 0 : 1);
}

main().catch((error) => {
  console.log(JSON.stringify({ schema: "simplicio.opencode-host-harness/v1", ok: false, error: String(error?.stack || error) }));
  process.exit(1);
});
