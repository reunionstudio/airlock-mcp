import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import {
  codexInstallArgs,
  codexInstallCommand,
  installCodexServer,
  validatePackageSpec,
  validateServerName,
} from "../src/install.mjs";
import { encodeMessage, handleMcpRequest, makeError } from "../src/mcp.mjs";
import { specsRepoName } from "../src/text.mjs";

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

assert.equal(specsRepoName("Home"), "home-specs");
assert.equal(specsRepoName("home-specs"), "home-specs");
assert.deepEqual(codexInstallArgs("airlock"), ["mcp", "add", "airlock", "--", "npx", "-y", "@airlock/mcp", "server"]);
assert.equal(codexInstallCommand("airlock"), "codex mcp add airlock -- npx -y @airlock/mcp server");
assert.deepEqual(codexInstallArgs("airlock", "github:reunionstudio/airlock-mcp"), [
  "mcp",
  "add",
  "airlock",
  "--",
  "npx",
  "-y",
  "github:reunionstudio/airlock-mcp",
  "server",
]);
assert.equal(
  codexInstallCommand("airlock", "github:reunionstudio/airlock-mcp"),
  "codex mcp add airlock -- npx -y github:reunionstudio/airlock-mcp server",
);
assert.equal(validateServerName("airlock.dev"), "airlock.dev");
assert.throws(() => validateServerName("airlock; rm -rf"), /server name/);
assert.equal(validatePackageSpec("github:reunionstudio/airlock-mcp"), "github:reunionstudio/airlock-mcp");
assert.throws(() => validatePackageSpec("bad\npackage"), /package spec/);
assert.throws(() => validatePackageSpec("bad package"), /package spec/);
const directInstall = installCodexServer({
  packageSpec: "github:reunionstudio/airlock-mcp",
  beforeRun: () => assert.fail("dry run should not call beforeRun"),
  dryRun: true,
});
assert.equal(directInstall.status, 0);
assert.match(directInstall.stdout, /github:reunionstudio\/airlock-mcp/);
assert.deepEqual(makeError(null, -32700, "parse error"), {
  jsonrpc: "2.0",
  id: null,
  error: { code: -32700, message: "parse error" },
});
assert.doesNotMatch(encodeMessage({ jsonrpc: "2.0", id: 1, result: { text: "a\nb" } }).slice(0, -1), /\n/);
assert.equal(handleMcpRequest({ jsonrpc: "2.0", method: "notifications/initialized", params: {} }), undefined);
assert.equal(handleMcpRequest({ jsonrpc: "2.0", id: 99, method: "unknown/method" }).error.code, -32601);
assert.equal(
  handleMcpRequest({
    jsonrpc: "2.0",
    id: 100,
    method: "tools/call",
    params: { name: "nope", arguments: {} },
  }).error.code,
  -32602,
);

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
  { jsonrpc: "2.0", method: "notifications/initialized", params: {} },
  { jsonrpc: "2.0", id: 8, method: "unknown/method", params: {} },
]
  .map((message) => JSON.stringify(message))
  .concat("not-json")
  .join("\n");

const server = run(["server"], `${input}\n`);
assert.equal(server.status, 0, server.stderr);
assert.equal(server.stderr, "");

const responses = server.stdout
  .trim()
  .split("\n")
  .filter(Boolean)
  .map((line) => JSON.parse(line));

assert.equal(responses.length, 9);
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
assert.equal(responses[7].error.code, -32601);
assert.equal(responses[8].error.code, -32700);

const invalidInstall = run(["install", "--name", "airlock;bad", "--dry-run"]);
assert.equal(invalidInstall.status, 2);
assert.match(invalidInstall.stderr, /server name/);

const missingName = run(["install", "--name"]);
assert.equal(missingName.status, 2);
assert.match(missingName.stderr, /--name requires a value/);

const missingPackage = run(["install", "--package"]);
assert.equal(missingPackage.status, 2);
assert.match(missingPackage.stderr, /--package requires a value/);
