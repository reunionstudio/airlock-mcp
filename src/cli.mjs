import { DEFAULT_PACKAGE_SPEC, DEFAULT_SERVER_NAME, helpText } from "./text.mjs";
import { installCodexServer } from "./install.mjs";
import { runServer } from "./mcp.mjs";

export function parseArgs(argv) {
  const parsed = {
    command: argv[0],
    project: "Home",
    serverName: DEFAULT_SERVER_NAME,
    packageSpec: DEFAULT_PACKAGE_SPEC,
    dryRun: false,
    help: false,
  };
  for (let index = 1; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--help" || arg === "-h") {
      parsed.help = true;
    } else if (arg === "--project") {
      if (!argv[index + 1] || argv[index + 1].startsWith("--")) {
        throw new Error("--project requires a value");
      }
      parsed.project = argv[index + 1] || parsed.project;
      index += 1;
    } else if (arg === "--name") {
      if (!argv[index + 1] || argv[index + 1].startsWith("--")) {
        throw new Error("--name requires a value");
      }
      parsed.serverName = argv[index + 1] || parsed.serverName;
      index += 1;
    } else if (arg === "--package") {
      if (!argv[index + 1] || argv[index + 1].startsWith("--")) {
        throw new Error("--package requires a value");
      }
      parsed.packageSpec = argv[index + 1] || parsed.packageSpec;
      index += 1;
    } else if (arg === "--dry-run") {
      parsed.dryRun = true;
    } else {
      throw new Error(`unknown argument: ${arg}`);
    }
  }
  return parsed;
}

export async function main(argv = process.argv.slice(2), io = process) {
  let args;
  try {
    args = parseArgs(argv);
  } catch (error) {
    io.stderr.write(`error: ${error.message}\n`);
    return 2;
  }

  if (!args.command || args.help) {
    io.stdout.write(helpText());
    return 0;
  }

  if (args.command === "install") {
    try {
      const result = installCodexServer({
        project: args.project,
        serverName: args.serverName,
        packageSpec: args.packageSpec,
        dryRun: args.dryRun,
        beforeRun: (text) => io.stdout.write(text),
      });
      if (result.stdout) {
        io.stdout.write(result.stdout);
      }
      if (result.stderr) {
        io.stderr.write(result.stderr);
      }
      return result.status;
    } catch (error) {
      io.stderr.write(`error: ${error.message}\n`);
      return 2;
    }
  }

  if (args.command === "server") {
    await runServer();
    return 0;
  }

  io.stderr.write(`error: unknown command: ${args.command}\n`);
  io.stdout.write(helpText());
  return 2;
}
