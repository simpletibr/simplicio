#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const path = require("node:path");
const { test } = require("node:test");

const launcher = require("./simplicio/install.js");
const fs = require("node:fs");
const pathModule = require("node:path");

function launcherSource(relative) {
  return fs.readFileSync(pathModule.join(__dirname, relative), "utf8");
}

test("every npm entry point ships the same managed launcher", () => {
  const canonical = launcherSource("simplicio/install.js");
  assert.equal(launcherSource("simplicio-installer/install.js"), canonical);
  assert.equal(launcherSource("simplicio-unscoped/install.js"), canonical);
});


function silentLog() {
  return { log() {}, error() {} };
}

test("managed binary lives under ~/.simplicio/bin on every platform", () => {
  assert.equal(
    launcher.managedBinary({ platform: "linux", env: {}, home: "/home/u" }),
    path.join("/home/u", ".simplicio", "bin", "simplicio"),
  );
  assert.equal(
    launcher.managedBinary({ platform: "darwin", env: {}, home: "/Users/u" }),
    path.join("/Users/u", ".simplicio", "bin", "simplicio"),
  );
  assert.equal(
    launcher.managedBinary({ platform: "win32", env: {}, home: "C:/Users/u" }),
    path.join("C:/Users/u", ".simplicio", "bin", "simplicio.exe"),
  );
});

test("SIMPLICIO_BIN and SIMPLICIO_BIN_DIR are honored", () => {
  assert.equal(
    launcher.managedBinary({ platform: "linux", env: { SIMPLICIO_BIN: "/opt/simplicio" }, home: "/home/u" }),
    "/opt/simplicio",
  );
  assert.equal(
    launcher.managedBinary({
      platform: "linux",
      env: { SIMPLICIO_BIN_DIR: "/opt/bin" },
      home: "/home/u",
    }),
    path.join("/opt/bin", "simplicio"),
  );
});

test("an installed binary is launched with the caller arguments", () => {
  const calls = [];
  const status = launcher.main({
    argv: ["status", "--json"],
    platform: "linux",
    env: {},
    home: "/home/u",
    exists: () => true,
    execute: () => {
      throw new Error("installer must not run when the managed binary exists");
    },
    spawn: (binary, argv, options) => {
      calls.push({ binary, argv, options });
      return { status: 7 };
    },
    log: silentLog(),
    packageName: "@simpletibr/simplicio",
  });

  assert.equal(status, 7);
  assert.deepEqual(calls, [
    {
      binary: path.join("/home/u", ".simplicio", "bin", "simplicio"),
      argv: ["status", "--json"],
      options: { stdio: "inherit" },
    },
  ]);
});

test("a missing binary installs once and then launches", () => {
  const executed = [];
  const spawned = [];
  let installed = false;
  const status = launcher.main({
    argv: ["chat", "hello"],
    platform: "linux",
    env: {},
    home: "/home/u",
    exists: () => installed,
    execute: (command) => {
      executed.push(command);
      installed = true;
    },
    spawn: (binary, argv) => {
      spawned.push({ binary, argv });
      return { status: 0 };
    },
    log: silentLog(),
    packageName: "@simpletibr/simplicio",
  });

  assert.equal(status, 0);
  assert.equal(executed.length, 1);
  assert.match(executed[0], /install\.sh/);
  assert.deepEqual(spawned, [
    {
      binary: path.join("/home/u", ".simplicio", "bin", "simplicio"),
      argv: ["chat", "hello"],
    },
  ]);
});

test("simplicio-installer without arguments installs but does not launch", () => {
  const executed = [];
  let spawned = false;
  let installed = false;
  const status = launcher.main({
    argv: [],
    platform: "linux",
    env: {},
    home: "/home/u",
    exists: () => installed,
    execute: (command) => {
      executed.push(command);
      installed = true;
    },
    spawn: () => {
      spawned = true;
      return { status: 0 };
    },
    log: silentLog(),
    packageName: "simplicio-installer",
  });

  assert.equal(status, 0);
  assert.equal(executed.length, 1);
  assert.equal(spawned, false);
});

test("a fresh no-argument invocation installs and exits without launching", () => {
  const executed = [];
  let spawned = false;
  let installed = false;
  const status = launcher.main({
    argv: [],
    platform: "linux",
    env: {},
    home: "/home/u",
    exists: () => installed,
    execute: (command) => {
      executed.push(command);
      installed = true;
    },
    spawn: () => {
      spawned = true;
      return { status: 0 };
    },
    log: silentLog(),
    packageName: "@simpletibr/simplicio",
  });

  assert.equal(status, 0);
  assert.equal(executed.length, 1);
  assert.equal(spawned, false);
});

test("dry run never installs or launches", () => {
  const executed = [];
  let spawned = false;
  const status = launcher.main({
    argv: ["status"],
    platform: "win32",
    env: {},
    home: "C:/Users/u",
    exists: () => false,
    dryRun: true,
    execute: (command) => executed.push(command),
    spawn: () => {
      spawned = true;
      return { status: 0 };
    },
    log: silentLog(),
    packageName: "@simpletibr/simplicio",
  });

  assert.equal(status, 0);
  assert.deepEqual(executed, []);
  assert.equal(spawned, false);
});
