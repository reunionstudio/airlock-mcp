import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const bin = fileURLToPath(new URL("../bin/airlock-mcp.mjs", import.meta.url));

function run(args, input) {
  return spawnSync(process.execPath, [bin, ...args], {
    input,
    encoding: "utf8",
  });
}

const install = run(["install", "--project", "Home", "--dry-run"]);
assert.equal(install.status, 0, install.stderr);
assert.match(install.stdout, /codex mcp add airlock -- npx -y @airlock\/mcp server/);
assert.match(install.stdout, /home-specs/);
assert.match(install.stdout, /Do not create/);

const input = [
  {
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {
      protocolVersion: "2025-06-18",
      capabilities: {},
      clientInfo: { name: "test", version: "0.1.0" },
    },
  },
  { jsonrpc: "2.0", id: 2, method: "tools/list", params: {} },
  { jsonrpc: "2.0", id: 3, method: "prompts/list", params: {} },
  { jsonrpc: "2.0", id: 4, method: "resources/list", params: {} },
]
  .map((message) => JSON.stringify(message))
  .join("\n");

const server = run(["server"], `${input}\n`);
assert.equal(server.status, 0, server.stderr);

const responses = server.stdout
  .trim()
  .split("\n")
  .filter(Boolean)
  .map((line) => JSON.parse(line));

assert.equal(responses.length, 4);
assert.equal(responses[0].result.serverInfo.name, "airlock");
assert.equal(responses[1].result.tools[0].name, "airlock_smith_start");
assert.equal(responses[2].result.prompts[0].name, "airlock-smith-start");
assert.equal(responses[3].result.resources[0].uri, "airlock://smith/getting-started");
