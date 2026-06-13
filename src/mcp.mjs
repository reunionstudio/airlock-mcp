import readline from "node:readline";

import { PROTOCOL_VERSION, airlockPrompt, gettingStartedText } from "./text.mjs";

const GETTING_STARTED_URI = "airlock://getting-started";

export function makeResponse(id, result) {
  return { jsonrpc: "2.0", id, result };
}

export function makeError(id, code, message) {
  return { jsonrpc: "2.0", id, error: { code, message } };
}

export function handleMcpRequest(message) {
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
      instructions:
        "Airlock MCP helps agents build and use Airlock specs. Use airlock_start to begin in a specs repo.",
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
                maxLength: 80,
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
      content: [{ type: "text", text: gettingStartedText(project) }],
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
          uri: GETTING_STARTED_URI,
          name: "Airlock getting started",
          description: "How to start building and using Airlock specs with Codex.",
          mimeType: "text/markdown",
        },
      ],
    });
  }

  if (method === "resources/read") {
    if (params?.uri !== GETTING_STARTED_URI) {
      return makeError(id, -32602, `unknown resource: ${params?.uri || ""}`);
    }
    return makeResponse(id, {
      contents: [
        {
          uri: params.uri,
          mimeType: "text/markdown",
          text: gettingStartedText("Home"),
        },
      ],
    });
  }

  return makeError(id, -32601, `method not found: ${method}`);
}

export function encodeMessage(message) {
  return `${JSON.stringify(message)}\n`;
}

export async function runServer({ input = process.stdin, output = process.stdout } = {}) {
  const rl = readline.createInterface({
    input,
    crlfDelay: Infinity,
  });

  for await (const line of rl) {
    if (!line.trim()) {
      continue;
    }

    let message;
    try {
      message = JSON.parse(line);
    } catch (_error) {
      output.write(encodeMessage(makeError(null, -32700, "parse error")));
      continue;
    }

    if (message.id === undefined) {
      handleMcpRequest(message);
      continue;
    }

    try {
      const response = handleMcpRequest(message);
      if (response) {
        output.write(encodeMessage(response));
      }
    } catch (error) {
      output.write(encodeMessage(makeError(message.id, -32603, error.message)));
    }
  }
}
