// Simplicio OpenCode plugin (#450).
//
// OpenCode V2 loads a plugin directory, reads the default export, and requires
// an object with `id` plus `setup` (or `effect`). V1 hosts call `server()` and
// use the returned hooks. Both paths share one enforcement function so a host
// upgrade cannot silently drop the gate.
//
// The pre-hook is the enforcement point for host-native programming tools:
// native file and shell tools are rejected with an actionable error naming the
// governed Simplicio MCP tool. Third-party MCP tools and unrelated plugins are
// untouched because only these native names are matched.

export const NATIVE_TOOL_ROUTES = Object.freeze({
  read: "simplicio_file",
  read_file: "simplicio_file",
  grep: "simplicio_file",
  glob: "simplicio_file",
  list: "simplicio_file",
  write: "simplicio_edit",
  write_file: "simplicio_edit",
  edit: "simplicio_edit",
  edit_file: "simplicio_edit",
  multiedit: "simplicio_edit",
  patch: "simplicio_edit",
  apply_patch: "simplicio_edit",
  shell: "simplicio_exec",
  bash: "simplicio_exec",
  exec: "simplicio_exec",
});

const REASON =
  "Simplicio is mandatory for this host: use %TOOL% instead of native %NATIVE%. " +
  "Orient with simplicio_map/simplicio_context first. Governed writes return a " +
  "simplicio.effect-receipt/v1 with a write_set. Third-party MCP tools and " +
  "unrelated plugins remain available.";

export function nativeRoute(tool) {
  const name = String(tool ?? "").trim().toLowerCase();
  if (!name) return undefined;
  return Object.prototype.hasOwnProperty.call(NATIVE_TOOL_ROUTES, name)
    ? NATIVE_TOOL_ROUTES[name]
    : undefined;
}

export function rejectionMessage(tool, replacement) {
  return REASON.replace("%TOOL%", replacement).replace("%NATIVE%", String(tool));
}

// Throws for a host-native programming tool. Any tool that is not in the table
// (simplicio_*, third-party MCP tools, unrelated host tools) passes through.
export function enforceNativeTool(tool) {
  const replacement = nativeRoute(tool);
  if (!replacement) return;
  throw new Error(rejectionMessage(tool, replacement));
}

const hooks = Object.freeze({
  "tool.execute.before": async (input) => enforceNativeTool(input?.tool),
});

export default {
  id: "simplicio",

  // OpenCode V2 hook registration.
  async setup(ctx) {
    const hook = ctx?.tool?.hook;
    if (typeof hook !== "function") {
      throw new Error(
        "Simplicio could not register its enforcement hook: the OpenCode V2 " +
          "plugin context does not expose tool.hook(). Refusing to load a " +
          "plugin that would silently allow native write/edit/shell tools.",
      );
    }
    await hook.call(ctx.tool, "execute.before", (event) => {
      enforceNativeTool(event?.tool);
    });
  },

  // OpenCode V1 compatibility.
  async server() {
    return { ...hooks };
  },
};
