import { existsSync, statSync } from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const MAX_ARG_LENGTH = 1000;
const OUTPUT_MAX_BUFFER = 1024 * 1024 * 4;

const cwdProperty = {
  type: "string",
  description: "Directory to run from. Defaults to the MCP server working directory.",
  maxLength: MAX_ARG_LENGTH,
};

const forceProperty = {
  type: "boolean",
  description: "Overwrite existing generated files when the underlying command supports it.",
};

const workspaceProperty = {
  type: "string",
  description: "Workspace path, such as workspaces/feedback-loop.",
  maxLength: MAX_ARG_LENGTH,
};

const appModeValues = ["spec-first", "app-first", "co-development"];

export const WORKBENCH_TOOLS = [
  {
    name: "airlock_doctor",
    description: "Check that bundled Airlock MCP workbench assets are available.",
    inputSchema: objectSchema({ cwd: cwdProperty }),
  },
  {
    name: "airlock_init_repo",
    description: "Bootstrap a Git-backed specs repo with AGENTS.md, the Airlock MCP skill, and workspaces/.",
    inputSchema: objectSchema({
      path: {
        type: "string",
        description: "Specs repo path to initialize. Defaults to the current directory.",
        maxLength: MAX_ARG_LENGTH,
      },
      force: forceProperty,
      cwd: cwdProperty,
    }),
  },
  {
    name: "airlock_init_app_context",
    description: "Seed an app repo with airlock/ spec snapshots, samples, generated placeholders, and a manifest.",
    inputSchema: objectSchema({
      path: {
        type: "string",
        description: "App repo path to initialize. Defaults to the current directory.",
        maxLength: MAX_ARG_LENGTH,
      },
      mode: {
        type: "string",
        enum: appModeValues,
        description: "Development mode. Defaults to app-first.",
      },
      specs: {
        type: "array",
        items: {
          type: "string",
          maxLength: MAX_ARG_LENGTH,
        },
        description: "Spec workspace directories or spec JSON files to snapshot.",
      },
      force: forceProperty,
      cwd: cwdProperty,
    }),
  },
  {
    name: "airlock_list_patterns",
    description: "List bundled Airlock spec starter patterns.",
    inputSchema: objectSchema({ cwd: cwdProperty }),
  },
  {
    name: "airlock_show_pattern",
    description: "Show a bundled starter pattern README or its file paths.",
    inputSchema: objectSchema(
      {
        pattern: {
          type: "string",
          enum: ["blank", "okf-knowledge-bundle", "posts"],
          description: "Pattern to inspect.",
        },
        files: {
          type: "boolean",
          description: "Print pattern file paths instead of the README.",
        },
        cwd: cwdProperty,
      },
      ["pattern"],
    ),
  },
  {
    name: "airlock_init_workspace",
    description: "Create a spec workspace from a bundled pattern.",
    inputSchema: objectSchema(
      {
        name: {
          type: "string",
          description: "Workspace folder name, such as feedback-loop.",
          maxLength: 160,
        },
        pattern: {
          type: "string",
          enum: ["blank", "okf-knowledge-bundle", "posts"],
          description: "Starting pattern. Defaults to blank.",
        },
        output: {
          type: "string",
          description: "Parent directory for the workspace. Defaults to ./workspaces.",
          maxLength: MAX_ARG_LENGTH,
        },
        force: forceProperty,
        cwd: cwdProperty,
      },
      ["name"],
    ),
  },
  {
    name: "airlock_list_workspaces",
    description: "List active or archived Airlock spec workspaces.",
    inputSchema: objectSchema({
      root: {
        type: "string",
        description: "Workspace root. Defaults to ./workspaces.",
        maxLength: MAX_ARG_LENGTH,
      },
      all: {
        type: "boolean",
        description: "Include archived workspaces.",
      },
      paths: {
        type: "boolean",
        description: "Print only workspace paths.",
      },
      cwd: cwdProperty,
    }),
  },
  {
    name: "airlock_check_workspace",
    description: "Run local validation against a spec workspace.",
    inputSchema: objectSchema({ workspace: workspaceProperty, cwd: cwdProperty }, ["workspace"]),
  },
  {
    name: "airlock_summary",
    description: "Summarize a spec workspace for session re-entry.",
    inputSchema: objectSchema({ workspace: workspaceProperty, cwd: cwdProperty }, ["workspace"]),
  },
  {
    name: "airlock_next",
    description: "Show the next safe action for a spec workspace.",
    inputSchema: objectSchema({ workspace: workspaceProperty, cwd: cwdProperty }, ["workspace"]),
  },
  {
    name: "airlock_export_csv",
    description: "Render sample.records.json as Airlock-ready CSV.",
    inputSchema: objectSchema(
      {
        workspace: workspaceProperty,
        output: {
          type: "string",
          description: "Optional output CSV path. If omitted, CSV is returned in tool output.",
          maxLength: MAX_ARG_LENGTH,
        },
        force: forceProperty,
        cwd: cwdProperty,
      },
      ["workspace"],
    ),
  },
  {
    name: "airlock_render_sql",
    description: "Render validate-only Airlock admin SQL for a workspace.",
    inputSchema: objectSchema(
      {
        workspace: workspaceProperty,
        app: {
          type: "string",
          description: "Installed Airlock app name. Defaults to airlock.",
          maxLength: 160,
        },
        operation: {
          type: "string",
          enum: ["create", "alter"],
          description: "Procedure shape to render. Defaults to create.",
        },
        force: forceProperty,
        cwd: cwdProperty,
      },
      ["workspace"],
    ),
  },
];

const WORKBENCH_TOOL_NAMES = new Set(WORKBENCH_TOOLS.map((tool) => tool.name));

function objectSchema(properties, required = []) {
  return {
    type: "object",
    properties,
    required,
    additionalProperties: false,
  };
}

export function packageRoot() {
  return path.resolve(fileURLToPath(new URL("..", import.meta.url)));
}

function optionalString(args, name, fallback) {
  const value = args?.[name];
  if (value === undefined || value === null || value === "") {
    return fallback;
  }
  if (typeof value !== "string") {
    throw new Error(`${name} must be a string`);
  }
  if (value.length > MAX_ARG_LENGTH || /[\u0000-\u001f\u007f]/.test(value)) {
    throw new Error(`${name} must be ${MAX_ARG_LENGTH} characters or fewer with no control characters`);
  }
  if (value.startsWith("-")) {
    throw new Error(`${name} must not start with '-'`);
  }
  return value;
}

function requiredString(args, name) {
  const value = optionalString(args, name, undefined);
  if (!value) {
    throw new Error(`${name} is required`);
  }
  return value;
}

function optionalBoolean(args, name, fallback = false) {
  const value = args?.[name];
  if (value === undefined || value === null) {
    return fallback;
  }
  if (typeof value !== "boolean") {
    throw new Error(`${name} must be a boolean`);
  }
  return value;
}

function optionalEnum(args, name, allowed, fallback) {
  const value = optionalString(args, name, fallback);
  if (value === undefined) {
    return fallback;
  }
  if (!allowed.includes(value)) {
    throw new Error(`${name} must be one of: ${allowed.join(", ")}`);
  }
  return value;
}

function optionalStringArray(args, name) {
  const value = args?.[name];
  if (value === undefined || value === null) {
    return [];
  }
  if (!Array.isArray(value)) {
    throw new Error(`${name} must be an array`);
  }
  return value.map((entry, index) => {
    if (typeof entry !== "string") {
      throw new Error(`${name}[${index}] must be a string`);
    }
    if (entry.length > MAX_ARG_LENGTH || /[\u0000-\u001f\u007f]/.test(entry)) {
      throw new Error(`${name}[${index}] must be ${MAX_ARG_LENGTH} characters or fewer with no control characters`);
    }
    if (entry.startsWith("-")) {
      throw new Error(`${name}[${index}] must not start with '-'`);
    }
    return entry;
  });
}

function requiredEnum(args, name, allowed) {
  const value = optionalEnum(args, name, allowed, undefined);
  if (value === undefined) {
    throw new Error(`${name} is required`);
  }
  return value;
}

function resolveCwd(args) {
  const cwd = optionalString(args, "cwd", process.cwd());
  const resolved = path.resolve(cwd);
  if (!existsSync(resolved) || !statSync(resolved).isDirectory()) {
    throw new Error(`cwd is not a directory: ${cwd}`);
  }
  return resolved;
}

function maybePush(args, flag, value) {
  if (value !== undefined && value !== null && value !== "") {
    args.push(flag, value);
  }
}

function cliArgsForTool(name, args = {}) {
  const cwd = resolveCwd(args);
  const force = optionalBoolean(args, "force");
  switch (name) {
    case "airlock_doctor":
      return { cwd, cliArgs: ["doctor"] };
    case "airlock_init_repo": {
      const cliArgs = ["init-repo", optionalString(args, "path", ".")];
      if (force) cliArgs.push("--force");
      return { cwd, cliArgs };
    }
    case "airlock_init_app_context": {
      const cliArgs = [
        "init-app-context",
        optionalString(args, "path", "."),
        "--mode",
        optionalEnum(args, "mode", appModeValues, "app-first"),
      ];
      for (const spec of optionalStringArray(args, "specs")) {
        cliArgs.push("--spec", spec);
      }
      if (force) cliArgs.push("--force");
      return { cwd, cliArgs };
    }
    case "airlock_list_patterns":
      return { cwd, cliArgs: ["list-patterns"] };
    case "airlock_show_pattern": {
      const cliArgs = ["show-pattern", requiredEnum(args, "pattern", ["blank", "posts"])];
      if (optionalBoolean(args, "files")) cliArgs.push("--files");
      return { cwd, cliArgs };
    }
    case "airlock_init_workspace": {
      const cliArgs = ["init", requiredString(args, "name"), "--pattern", optionalEnum(args, "pattern", ["blank", "posts"], "blank")];
      maybePush(cliArgs, "--output", optionalString(args, "output", undefined));
      if (force) cliArgs.push("--force");
      return { cwd, cliArgs };
    }
    case "airlock_list_workspaces": {
      const cliArgs = ["list-workspaces"];
      maybePush(cliArgs, "--root", optionalString(args, "root", undefined));
      if (optionalBoolean(args, "all")) cliArgs.push("--all");
      if (optionalBoolean(args, "paths")) cliArgs.push("--paths");
      return { cwd, cliArgs };
    }
    case "airlock_check_workspace":
      return { cwd, cliArgs: ["check", requiredString(args, "workspace")] };
    case "airlock_summary":
      return { cwd, cliArgs: ["summary", requiredString(args, "workspace")] };
    case "airlock_next":
      return { cwd, cliArgs: ["next", requiredString(args, "workspace")] };
    case "airlock_export_csv": {
      const cliArgs = ["export-csv", requiredString(args, "workspace")];
      maybePush(cliArgs, "--output", optionalString(args, "output", undefined));
      if (force) cliArgs.push("--force");
      return { cwd, cliArgs };
    }
    case "airlock_render_sql": {
      const cliArgs = ["render-sql", requiredString(args, "workspace")];
      maybePush(cliArgs, "--app", optionalString(args, "app", undefined));
      maybePush(cliArgs, "--operation", optionalEnum(args, "operation", ["create", "alter"], undefined));
      if (force) cliArgs.push("--force");
      return { cwd, cliArgs };
    }
    default:
      return undefined;
  }
}

export function runWorkbenchCli(cliArgs, { cwd, env = process.env, spawn = spawnSync } = {}) {
  const root = packageRoot();
  const python = env.AIRLOCK_MCP_PYTHON || env.PYTHON || "python3";
  const pythonPath = [path.join(root, "src"), env.PYTHONPATH].filter(Boolean).join(path.delimiter);
  const result = spawn(python, ["-m", "airlock_mcp", ...cliArgs], {
    cwd,
    encoding: "utf8",
    maxBuffer: OUTPUT_MAX_BUFFER,
    env: {
      ...env,
      AIRLOCK_MCP_HOME: root,
      PYTHONPATH: pythonPath,
    },
  });

  if (result.error) {
    return {
      status: 127,
      stdout: "",
      stderr: `error: could not run ${python}: ${result.error.message}\n`,
    };
  }

  return {
    status: typeof result.status === "number" ? result.status : 1,
    stdout: result.stdout || "",
    stderr: result.stderr || "",
  };
}

export function callWorkbenchTool(name, args = {}) {
  if (!WORKBENCH_TOOL_NAMES.has(name)) {
    return undefined;
  }
  const plan = cliArgsForTool(name, args);
  const result = runWorkbenchCli(plan.cliArgs, { cwd: plan.cwd });
  return formatCliToolResult(result);
}

function formatCliToolResult(result) {
  const chunks = [];
  if (result.stdout.trim()) {
    chunks.push(result.stdout.trimEnd());
  }
  if (result.stderr.trim()) {
    chunks.push(`stderr:\n${result.stderr.trimEnd()}`);
  }
  if (!chunks.length) {
    chunks.push(result.status === 0 ? "ok" : `airlock-mcp exited with status ${result.status}`);
  }
  if (result.status !== 0) {
    chunks.unshift(`airlock-mcp exited with status ${result.status}.`);
  }
  return {
    content: [{ type: "text", text: chunks.join("\n\n") }],
    ...(result.status === 0 ? {} : { isError: true }),
  };
}
