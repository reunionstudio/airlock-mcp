#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import readline from "node:readline";

const PACKAGE_NAME = "@airlock/mcp";
const DEFAULT_SERVER_NAME = "airlock";
const PROTOCOL_VERSION = "2025-06-18";

function printHelp() {
  console.log(`airlock-mcp

Usage:
  npx @airlock/mcp install [--project <name>] [--name <server-name>] [--dry-run]
  npx @airlock/mcp server

Commands:
  install   Register the Airlock MCP server with Codex.
  server    Run the Airlock MCP stdio server.

Options:
  --project <name>      Show next steps using <name>-specs.
  --name <server-name>  Codex MCP server name. Defaults to airlock.
  --dry-run             Print the Codex registration command without running it.
  --help                Show this help.

Airlock MCP is the single installed interface for agents working with Airlock.
Airlock Smith is the spec-building capability inside that experience.
`);
}

function slug(value) {
  const cleaned = String(value || "project")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return cleaned || "project";
}

function specsRepoName(project) {
  const value = slug(project);
  return value.endsWith("-specs") ? value : `${value}-specs`;
}

function shellQuote(value) {
  if (/^[a-zA-Z0-9_./:@=-]+$/.test(value)) {
    return value;
  }
  return `'${value.replace(/'/g, "'\\''")}'`;
}

function codexInstallArgs(serverName) {
  return ["mcp", "add", serverName, "--", "npx", "-y", PACKAGE_NAME, "server"];
}

function codexInstallCommand(serverName) {
  return ["codex", ...codexInstallArgs(serverName)].map(shellQuote).join(" ");
}

function airlockPrompt(project) {
  const repoName = specsRepoName(project);
  return `I want to use Airlock MCP to start working with Airlock specs for ${repoName}.

Set up this project as an Airlock specs repo. Use the Airlock Smith
spec-building capability when we need to draft or revise specs. Welcome me,
help me think through real Airlock use cases, and ask only for the missing
decisions. Do not create the first workspace until I choose a path.`;
}

function nextSteps(project) {
  const repoName = specsRepoName(project);
  return `Next:
  1. Open Codex.
  2. Create a new blank project named ${repoName}.
  3. Ask Codex:

${airlockPrompt(project)
  .split("\n")
  .map((line) => `     ${line}`)
  .join("\n")}

Airlock MCP will offer:
  - spec-building with Airlock Smith
  - guidance for using specs to pull and push governed data
  - improvement loops based on real Airlock use cases
  - OODA brainstorming for possible specs
  - a blank workspace for a known process
  - a posts feedback loop for shared human/agent feedback`;
}

function parseArgs(argv) {
  const parsed = {
    command: argv[0],
    project: "Home",
    serverName: DEFAULT_SERVER_NAME,
    dryRun: false,
    help: false,
  };
  for (let index = 1; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--help" || arg === "-h") {
      parsed.help = true;
    } else if (arg === "--project") {
      parsed.project = argv[index + 1] || parsed.project;
      index += 1;
    } else if (arg === "--name") {
      parsed.serverName = argv[index + 1] || parsed.serverName;
      index += 1;
    } else if (arg === "--dry-run") {
      parsed.dryRun = true;
    } else {
      throw new Error(`unknown argument: ${arg}`);
    }
  }
  return parsed;
}

function printInstall(project, serverName, dryRun) {
  const command = codexInstallCommand(serverName);
  console.log(`Airlock MCP install

Registering Codex MCP server:
  ${command}
`);

  if (dryRun) {
    console.log(`dry-run: not running registration.

${nextSteps(project)}
`);
    return 0;
  }

  const result = spawnSync("codex", codexInstallArgs(serverName), { stdio: "inherit" });
  if (result.error) {
    console.error(`error: could not run codex: ${result.error.message}`);
    console.error("Run this command manually after Codex is installed:");
    console.error(`  ${command}`);
    return 1;
  }
  if (result.status !== 0) {
    return result.status || 1;
  }

  console.log(`
installed: Codex MCP server '${serverName}'

${nextSteps(project)}
`);
  return 0;
}

function mcpText(project) {
  return `# Airlock MCP

Airlock MCP is the single installed interface for AI agents working with
Airlock. It helps a person and their agent build specs, pull and push governed data
through specs, and improve Airlock workflows from real use cases.

Airlock Smith is the spec-building capability inside Airlock MCP. Use it when a
spec needs to be drafted, checked, revised, imported, cloned, or prepared for
installed Airlock validation.

Start in a blank project specs repo such as ${specsRepoName(project)}. Do not
work inside the Airlock MCP or Airlock Smith implementation repos unless you
are changing the tools themselves.

Use this prompt in the blank specs repo:

${airlockPrompt(project)}

After bootstrap, choose the next useful path:

1. Brainstorm possible specs using the OODA loop.
2. Start from a known process and create a blank workspace.
3. Create a posts feedback loop for humans and agents to submit requests,
   observations, and responses.
4. Use an installed Airlock app to validate specs, load data, read outputs, or
   plan push/pull workflows through specs.

Create posts only when the user chooses the feedback-loop path.`;
}

function makeResponse(id, result) {
  return { jsonrpc: "2.0", id, result };
}

function makeError(id, code, message) {
  return { jsonrpc: "2.0", id, error: { code, message } };
}

function handleMcpRequest(message) {
  const { id, method, params } = message;

  if (method === "initialize") {
    return makeResponse(id, {
      protocolVersion: params?.protocolVersion || PROTOCOL_VERSION,
      capabilities: {
        prompts: {},
        resources: {},
        tools: {},
      },
      serverInfo: {
        name: "airlock",
        version: "0.1.0",
      },
    });
  }

  if (method === "notifications/initialized") {
    return undefined;
  }

  if (method === "tools/list") {
    return makeResponse(id, {
      tools: [
        {
          name: "airlock_start",
          description: "Return Airlock MCP setup guidance for building and using Airlock specs.",
          inputSchema: {
            type: "object",
            properties: {
              project: {
                type: "string",
                description: "Project or organization name, for example Home.",
              },
            },
            additionalProperties: false,
          },
        },
      ],
    });
  }

  if (method === "tools/call") {
    if (params?.name !== "airlock_start") {
      return makeError(id, -32602, `unknown tool: ${params?.name || ""}`);
    }
    const project = params?.arguments?.project || "Home";
    return makeResponse(id, {
      content: [{ type: "text", text: mcpText(project) }],
    });
  }

  if (method === "prompts/list") {
    return makeResponse(id, {
      prompts: [
        {
          name: "airlock-start",
          title: "Start Airlock",
          description: "Bootstrap a blank specs repo and choose the first Airlock path.",
          arguments: [
            {
              name: "project",
              description: "Project or organization name, for example Home.",
              required: false,
            },
          ],
        },
      ],
    });
  }

  if (method === "prompts/get") {
    if (params?.name !== "airlock-start") {
      return makeError(id, -32602, `unknown prompt: ${params?.name || ""}`);
    }
    const project = params?.arguments?.project || "Home";
    return makeResponse(id, {
      description: "Start building and using Airlock specs in a blank specs repo.",
      messages: [
        {
          role: "user",
          content: { type: "text", text: airlockPrompt(project) },
        },
      ],
    });
  }

  if (method === "resources/list") {
    return makeResponse(id, {
      resources: [
        {
          uri: "airlock://getting-started",
          name: "Airlock getting started",
          description: "How to start building and using Airlock specs with Codex.",
          mimeType: "text/markdown",
        },
      ],
    });
  }

  if (method === "resources/read") {
    if (params?.uri !== "airlock://getting-started") {
      return makeError(id, -32602, `unknown resource: ${params?.uri || ""}`);
    }
    return makeResponse(id, {
      contents: [
        {
          uri: params.uri,
          mimeType: "text/markdown",
          text: mcpText("Home"),
        },
      ],
    });
  }

  return makeError(id, -32601, `method not found: ${method}`);
}

async function runServer() {
  const rl = readline.createInterface({
    input: process.stdin,
    crlfDelay: Infinity,
  });

  for await (const line of rl) {
    if (!line.trim()) {
      continue;
    }

    let message;
    try {
      message = JSON.parse(line);
    } catch (error) {
      process.stdout.write(`${JSON.stringify(makeError(null, -32700, "parse error"))}\n`);
      continue;
    }

    if (message.id === undefined) {
      handleMcpRequest(message);
      continue;
    }

    try {
      const response = handleMcpRequest(message);
      if (response) {
        process.stdout.write(`${JSON.stringify(response)}\n`);
      }
    } catch (error) {
      process.stdout.write(`${JSON.stringify(makeError(message.id, -32603, error.message))}\n`);
    }
  }
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(`error: ${error.message}`);
    process.exitCode = 2;
    return;
  }

  if (!args.command || args.help) {
    printHelp();
    return;
  }

  if (args.command === "install") {
    process.exitCode = printInstall(args.project, args.serverName, args.dryRun);
    return;
  }

  if (args.command === "server") {
    await runServer();
    return;
  }

  console.error(`error: unknown command: ${args.command}`);
  printHelp();
  process.exitCode = 2;
}

await main();
