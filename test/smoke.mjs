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
assert.match(install.stdout, /Airlock MCP will offer/);
assert.match(install.stdout, /using specs to pull and push governed data/);

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
  {
    jsonrpc: "2.0",
    id: 5,
    method: "tools/call",
    params: { name: "airlock_start", arguments: { project: "Home" } },
  },
  {
    jsonrpc: "2.0",
    id: 6,
    method: "prompts/get",
    params: { name: "airlock-start", arguments: { project: "Home" } },
  },
  {
    jsonrpc: "2.0",
    id: 7,
    method: "resources/read",
    params: { uri: "airlock://getting-started" },
  },
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

assert.equal(responses.length, 7);
assert.equal(responses[0].result.serverInfo.name, "airlock");
assert.equal(responses[1].result.tools[0].name, "airlock_start");
assert.equal(responses[1].result.tools[0].description, "Return Airlock MCP setup guidance for building and using Airlock specs.");
assert.equal(responses[2].result.prompts[0].name, "airlock-start");
assert.equal(responses[2].result.prompts[0].title, "Start Airlock");
assert.equal(responses[3].result.resources[0].uri, "airlock://getting-started");
assert.equal(responses[3].result.resources[0].name, "Airlock getting started");
assert.match(responses[4].result.content[0].text, /single installed interface/);
assert.match(responses[4].result.content[0].text, /pull and push governed data/);
assert.match(responses[5].result.messages[0].content.text, /Airlock MCP/);
assert.match(responses[6].result.contents[0].text, /Airlock Smith is the spec-building capability/);
