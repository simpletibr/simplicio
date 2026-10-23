#!/usr/bin/env node
"use strict";

const { execSync, spawnSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

// Every channel converges on this one managed binary. The npm entry point is
// a thin launcher, never a second copy and never an implicit reinstall.
function managedBinary({
  platform = os.platform(),
  env = process.env,
  home = os.homedir(),
} = {}) {
  if (env.SIMPLICIO_BIN) return env.SIMPLICIO_BIN;
  const dir = env.SIMPLICIO_BIN_DIR || path.join(home, ".simplicio", "bin");
  return path.join(dir, platform === "win32" ? "simplicio.exe" : "simplicio");
}

function installerCommand(platform = os.platform()) {
  return platform === "win32"
    ? 'powershell -c "irm https://simpleti.com.br/simplicio/install.ps1 | iex"'
    : "curl -fsSL https://simpleti.com.br/simplicio/install.sh | sh";
}

function runBinary(binary, argv, { spawn = spawnSync, log = console } = {}) {
  const result = spawn(binary, argv, { stdio: "inherit" });
  if (result.error) {
    log.error(`\n❌ Could not run ${binary}: ${result.error.message}`);
    return 1;
  }
  return typeof result.status === "number" ? result.status : 1;
}

function main({
  argv = process.argv.slice(2),
  platform = os.platform(),
  execute = execSync,
  spawn = spawnSync,
  env = process.env,
  home = os.homedir(),
  exists = fs.existsSync,
  dryRun = env.SIMPLICIO_INSTALL_DRY_RUN === "1",
  log = console,
  packageName = require("./package.json").name,
} = {}) {
  const binary = managedBinary({ platform, env, home });
  const installerOnly = packageName === "simplicio-installer" && argv.length === 0;
  const wantsInstall = argv[0] === "install" || installerOnly;

  if (!wantsInstall && exists(binary)) {
    return runBinary(binary, argv, { spawn, log });
  }

  const command = installerCommand(platform);
  log.log(
    `Installing the managed Simplicio Runtime for ${platform === "win32" ? "Windows" : "macOS/Linux"}...`,
  );
  if (dryRun) {
    log.log(`[DRY RUN] ${command}`);
    log.log(`[DRY RUN] managed binary: ${binary}`);
    return 0;
  }

  try {
    execute(command, { stdio: "inherit" });
  } catch (err) {
    log.error("\n❌ Installation failed:", err.message);
    return 1;
  }

  if (!exists(binary)) {
    log.error(`\n❌ Installer finished but the managed binary is missing: ${binary}`);
    return 1;
  }

  if (wantsInstall || argv.length === 0) {
    log.log("\n✅ Simplicio installed successfully!");
    log.log(`   Binary: ${binary}`);
    log.log("   Run: simplicio chat");
    log.log("   Docs: https://simpleti.com.br/simplicio/#start");
    return 0;
  }

  return runBinary(binary, argv, { spawn, log });
}

if (require.main === module) process.exitCode = main();

module.exports = { installerCommand, managedBinary, main, runBinary };
