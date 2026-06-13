import { spawnSync } from "node:child_process";

import { DEFAULT_PACKAGE_SPEC, DEFAULT_SERVER_NAME, nextSteps } from "./text.mjs";

const SERVER_NAME_PATTERN = /^[a-zA-Z0-9._-]{1,64}$/;
const PACKAGE_SPEC_MAX_LENGTH = 200;

export function validateServerName(value) {
  if (!SERVER_NAME_PATTERN.test(value || "")) {
    throw new Error("server name must be 1-64 characters: letters, numbers, dot, underscore, or hyphen");
  }
  return value;
}

export function validatePackageSpec(value) {
  const packageSpec = String(value || "");
  if (
    packageSpec.length < 1 ||
    packageSpec.length > PACKAGE_SPEC_MAX_LENGTH ||
    /[\s\u0000-\u001f\u007f]/.test(packageSpec)
  ) {
    throw new Error("package spec must be 1-200 characters with no whitespace or control characters");
  }
  return packageSpec;
}

export function shellQuote(value) {
  if (/^[a-zA-Z0-9_./:@=-]+$/.test(value)) {
    return value;
  }
  return `'${value.replace(/'/g, "'\\''")}'`;
}

export function codexInstallArgs(serverName = DEFAULT_SERVER_NAME, packageSpec = DEFAULT_PACKAGE_SPEC) {
  return [
    "mcp",
    "add",
    validateServerName(serverName),
    "--",
    "npx",
    "-y",
    validatePackageSpec(packageSpec),
    "server",
  ];
}

export function codexInstallCommand(serverName = DEFAULT_SERVER_NAME, packageSpec = DEFAULT_PACKAGE_SPEC) {
  return ["codex", ...codexInstallArgs(serverName, packageSpec)].map(shellQuote).join(" ");
}

export function installCodexServer({
  project = "Home",
  serverName = DEFAULT_SERVER_NAME,
  packageSpec = DEFAULT_PACKAGE_SPEC,
  dryRun = false,
  beforeRun = () => {},
  spawn = spawnSync,
} = {}) {
  const command = codexInstallCommand(serverName, packageSpec);
  const intro = `Airlock MCP install

Registering Codex MCP server:
  ${command}
`;

  if (dryRun) {
    return {
      status: 0,
      stdout: `${intro}
dry-run: not running registration.

${nextSteps(project)}
`,
    };
  }

  beforeRun(`${intro}\n`);
  const result = spawn("codex", codexInstallArgs(serverName, packageSpec), { stdio: "inherit" });
  if (result.error) {
    return {
      status: 1,
      stderr: `error: could not run codex: ${result.error.message}
Run this command manually after Codex is installed:
  ${command}
`,
    };
  }
  if (result.status !== 0) {
    return { status: result.status || 1 };
  }

  return {
    status: 0,
    stdout: `
installed: Codex MCP server '${serverName}'

${nextSteps(project)}
`,
  };
}
