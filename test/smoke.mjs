import assert from "node:assert/strict";
import { existsSync, mkdtempSync, readFileSync, rmSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import {
  codexInstallArgs,
  codexInstallCommand,
  installCodexServer,
  validatePackageSpec,
  validateServerName,
} from "../src/install.mjs";
import { AIRLOCK_TOOLS, encodeMessage, handleMcpRequest, makeError } from "../src/mcp.mjs";
import { specsRepoName } from "../src/text.mjs";

const bin = fileURLToPath(new URL("../bin/airlock-mcp.mjs", import.meta.url));
const packageJson = JSON.parse(readFileSync(fileURLToPath(new URL("../package.json", import.meta.url)), "utf8"));

assert.equal(packageJson.name, "@reunionstudio/airlock-mcp");
assert.equal(packageJson.bin["airlock-mcp"], "bin/airlock-mcp.mjs");
assert.ok(statSync(bin).mode & 0o111, "bin/airlock-mcp.mjs should be executable");
for (const file of packageJson.files) {
  assert.ok(existsSync(fileURLToPath(new URL(`../${file}`, import.meta.url))), `package file entry exists: ${file}`);
}

function run(args, input) {
  return spawnSync(process.execPath, [bin, ...args], {
    input,
    encoding: "utf8",
  });
}

const install = run(["install", "--project", "Home", "--dry-run"]);
assert.equal(install.status, 0, install.stderr);
assert.match(install.stdout, /codex mcp add airlock -- npx -y @reunionstudio\/airlock-mcp server/);
assert.match(install.stdout, /home-specs/);
assert.match(install.stdout, /Git-backed specs repo/);
assert.match(install.stdout, /where the home-specs directory should live/);
assert.match(install.stdout, /Do not create/);
assert.match(install.stdout, /Airlock MCP will offer/);
assert.match(install.stdout, /process discovery before choosing a spec pattern/);
assert.match(install.stdout, /Airlock operating patterns/);
assert.match(install.stdout, /app and workflow coding against existing Airlock specs/);
assert.doesNotMatch(install.stdout, /Airlock Star/);

assert.equal(specsRepoName("Home"), "home-specs");
assert.equal(specsRepoName("home-specs"), "home-specs");
assert.deepEqual(codexInstallArgs("airlock"), ["mcp", "add", "airlock", "--", "npx", "-y", "@reunionstudio/airlock-mcp", "server"]);
assert.equal(codexInstallCommand("airlock"), "codex mcp add airlock -- npx -y @reunionstudio/airlock-mcp server");
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

const toolNames = AIRLOCK_TOOLS.map((tool) => tool.name);
assert.equal(toolNames[0], "airlock_start");
assert.ok(toolNames.includes("airlock_init_repo"));
assert.ok(toolNames.includes("airlock_init_app_context"));
assert.ok(toolNames.includes("airlock_init_workspace"));
assert.ok(toolNames.includes("airlock_check_workspace"));
assert.ok(toolNames.includes("airlock_export_csv"));
assert.ok(toolNames.includes("airlock_render_sql"));
assert.equal(AIRLOCK_TOOLS.find((tool) => tool.name === "airlock_init_workspace").inputSchema.required[0], "name");
assert.ok(
  AIRLOCK_TOOLS.find((tool) => tool.name === "airlock_init_workspace").inputSchema.properties.pattern.enum.includes(
    "okf-knowledge-bundle",
  ),
);

const patterns = handleMcpRequest({
  jsonrpc: "2.0",
  id: 101,
  method: "tools/call",
  params: { name: "airlock_list_patterns", arguments: {} },
});
assert.equal(patterns.result.isError, undefined);
assert.match(patterns.result.content[0].text, /blank/);
assert.match(patterns.result.content[0].text, /posts/);
assert.match(patterns.result.content[0].text, /okf-knowledge-bundle/);

const invalidToolArgs = handleMcpRequest({
  jsonrpc: "2.0",
  id: 102,
  method: "tools/call",
  params: { name: "airlock_check_workspace", arguments: {} },
});
assert.equal(invalidToolArgs.error.code, -32602);
assert.match(invalidToolArgs.error.message, /workspace is required/);

const tmpRoot = mkdtempSync(join(tmpdir(), "airlock-mcp-smoke-"));
try {
  const initRepo = handleMcpRequest({
    jsonrpc: "2.0",
    id: 103,
    method: "tools/call",
    params: { name: "airlock_init_repo", arguments: { cwd: tmpRoot, path: ".", force: true } },
  });
  assert.equal(initRepo.result.isError, undefined);
  assert.match(initRepo.result.content[0].text, /created AGENTS.md/);
  assert.ok(existsSync(join(tmpRoot, "AGENTS.md")));
  assert.ok(existsSync(join(tmpRoot, ".agents", "skills", "airlock-mcp", "SKILL.md")));

  const initWorkspace = handleMcpRequest({
    jsonrpc: "2.0",
    id: 104,
    method: "tools/call",
    params: { name: "airlock_init_workspace", arguments: { cwd: tmpRoot, name: "feedback-loop", pattern: "posts" } },
  });
  assert.equal(initWorkspace.result.isError, undefined);
  assert.match(initWorkspace.result.content[0].text, /feedback-loop/);

  const listWorkspaces = handleMcpRequest({
    jsonrpc: "2.0",
    id: 105,
    method: "tools/call",
    params: { name: "airlock_list_workspaces", arguments: { cwd: tmpRoot } },
  });
  assert.match(listWorkspaces.result.content[0].text, /feedback-loop/);

  const checkWorkspace = handleMcpRequest({
    jsonrpc: "2.0",
    id: 106,
    method: "tools/call",
    params: { name: "airlock_check_workspace", arguments: { cwd: tmpRoot, workspace: "workspaces/feedback-loop" } },
  });
  assert.equal(checkWorkspace.result.isError, undefined);
  assert.match(checkWorkspace.result.content[0].text, /^ok$/m);

  const summary = handleMcpRequest({
    jsonrpc: "2.0",
    id: 107,
    method: "tools/call",
    params: { name: "airlock_summary", arguments: { cwd: tmpRoot, workspace: "workspaces/feedback-loop" } },
  });
  assert.match(summary.result.content[0].text, /spec: posts \(Posts\)/);
  assert.match(summary.result.content[0].text, /core:/);
  assert.match(summary.result.content[0].text, /file_rules:/);
  assert.match(summary.result.content[0].text, /column_rules:/);
  assert.match(summary.result.content[0].text, /samples:/);
  assert.match(summary.result.content[0].text, /first_record_key: post_id=POST-001/);

  const csv = handleMcpRequest({
    jsonrpc: "2.0",
    id: 108,
    method: "tools/call",
    params: { name: "airlock_export_csv", arguments: { cwd: tmpRoot, workspace: "workspaces/feedback-loop" } },
  });
  assert.match(csv.result.content[0].text, /post_id,reply_to_post_id/);

  const sql = handleMcpRequest({
    jsonrpc: "2.0",
    id: 109,
    method: "tools/call",
    params: { name: "airlock_render_sql", arguments: { cwd: tmpRoot, workspace: "workspaces/feedback-loop" } },
  });
  assert.match(sql.result.content[0].text, /CALL airlock\.admin\.create_spec/);
  assert.match(sql.result.content[0].text, /TRUE\);/);

  const initAppContext = handleMcpRequest({
    jsonrpc: "2.0",
    id: 110,
    method: "tools/call",
    params: {
      name: "airlock_init_app_context",
      arguments: {
        cwd: tmpRoot,
        path: "app",
        mode: "co-development",
        specs: ["workspaces/feedback-loop"],
      },
    },
  });
  assert.equal(initAppContext.result.isError, undefined);
  assert.match(initAppContext.result.content[0].text, /initialized app context/);
  assert.match(initAppContext.result.content[0].text, /mode: co-development/);
  assert.match(initAppContext.result.content[0].text, /seeded_specs: posts/);
  assert.ok(existsSync(join(tmpRoot, "app", "airlock", "specs.manifest.json")));
  assert.ok(existsSync(join(tmpRoot, "app", "airlock", "spec-snapshots", "posts.spec.config.json")));
  assert.ok(existsSync(join(tmpRoot, "app", "airlock", "sample-records", "posts.sample.records.json")));
  const appManifest = JSON.parse(readFileSync(join(tmpRoot, "app", "airlock", "specs.manifest.json"), "utf8"));
  assert.equal(appManifest.mode, "co-development");
  assert.equal(appManifest.specs[0].snapshot_only, true);
} finally {
  rmSync(tmpRoot, { recursive: true, force: true });
}

const input = [
  {
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {
      protocolVersion: "2025-06-18",
      capabilities: {},
      clientInfo: { name: "test", version: "0.1.4" },
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
assert.equal(responses[0].result.serverInfo.version, "0.1.4");
assert.equal(responses[1].result.tools[0].name, "airlock_start");
assert.equal(responses[1].result.tools[0].description, "Return Airlock MCP setup guidance for specs and apps that use specs.");
assert.equal(responses[2].result.prompts[0].name, "airlock-start");
assert.equal(responses[2].result.prompts[0].title, "Start Airlock");
assert.equal(responses[3].result.resources[0].uri, "airlock://getting-started");
assert.equal(responses[3].result.resources[0].name, "Airlock getting started");
assert.match(responses[4].result.content[0].text, /single installed interface/);
assert.match(responses[4].result.content[0].text, /Git-backed specs repo/);
assert.match(responses[4].result.content[0].text, /ask where the directory should live/);
assert.match(responses[4].result.content[0].text, /App-first: build an app or workflow from existing specs/);
assert.match(responses[4].result.content[0].text, /co-development mode/);
assert.match(responses[4].result.content[0].text, /read specs/);
assert.match(responses[4].result.content[0].text, /observe\.\*/);
assert.match(responses[4].result.content[0].text, /observe\.explain_access/);
assert.match(responses[4].result.content[0].text, /direct table writes/);
assert.match(responses[4].result.content[0].text, /What process do you want to improve/);
assert.match(responses[4].result.content[0].text, /Airlock calls these places interfaces/);
assert.match(responses[4].result.content[0].text, /If you already have artifacts/);
assert.match(responses[4].result.content[0].text, /airlock-specs library/);
assert.doesNotMatch(responses[4].result.content[0].text, /Airlock Star/);
assert.match(responses[5].result.messages[0].content.text, /Airlock MCP/);
assert.match(responses[5].result.messages[0].content.text, /Git repo/);
assert.match(responses[5].result.messages[0].content.text, /where the home-specs/);
assert.match(responses[5].result.messages[0].content.text, /spec-first, app-first, or co-development/);
assert.match(responses[5].result.messages[0].content.text, /airlock-mcp init-app-context/);
assert.match(responses[5].result.messages[0].content.text, /airlock\.observe\.\*/);
assert.match(responses[5].result.messages[0].content.text, /observe\.governance_map/);
assert.match(responses[5].result.messages[0].content.text, /admin\.list_specs/);
assert.match(responses[5].result.messages[0].content.text, /approved\s+Airlock\/Snowflake access paths/);
assert.match(responses[5].result.messages[0].content.text, /process I want to improve/);
assert.match(responses[5].result.messages[0].content.text, /CSV or Excel files/);
assert.match(responses[5].result.messages[0].content.text, /airlock-specs library/);
assert.match(responses[6].result.contents[0].text, /Spec design: draft, check, revise/);
assert.match(responses[6].result.contents[0].text, /Airlock operating patterns/);
assert.match(responses[6].result.contents[0].text, /App and workflow implementation/);
assert.match(responses[6].result.contents[0].text, /Governance observation/);
assert.match(responses[6].result.contents[0].text, /If you already have artifacts/);
assert.doesNotMatch(responses[6].result.contents[0].text, /Airlock Star/);
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
