---
name: mcporter
description: 'Discover, call, and manage MCP servers via the mcporter CLI. Auto-discovers servers from Claude Desktop/Cursor configs. Connect to stdio or HTTP MCP servers. Use when managing MCP servers, calling MCP tools from CLI, or discovering available MCP integrations.'
interaction: autonomous
type: leaf
---

# mcporter — MCP Server Manager

Discover, call, and manage MCP (Model Context Protocol) servers from the command line.

## Prerequisites

```bash
# No install needed — runs via npx
npx mcporter
```

## Auto-Discovery

mcporter automatically discovers MCP servers configured by:

- Claude Desktop (`~/.config/claude/claude_desktop_config.json`)
- Cursor (`.cursor/mcp.json`)

```bash
# List discovered servers
npx mcporter list
```

## Connecting to Servers

```bash
# Connect to auto-discovered server
npx mcporter connect server-name

# Connect to HTTP MCP server
npx mcporter --http-url https://mcp-server.example.com

# Connect to stdio MCP server
npx mcporter --stdio "node /path/to/server.js"
```

## Calling Tools

```bash
# Key=value syntax
npx mcporter call server-name tool-name key1=value1 key2=value2

# Function syntax
npx mcporter call server-name "tool-name(arg1, arg2)"

# JSON args
npx mcporter call server-name tool-name --json '{"key": "value"}'

# JSON output
npx mcporter call server-name tool-name --output json
```

## Code Generation

```bash
# Generate CLI wrapper for a server
npx mcporter codegen cli server-name

# Generate TypeScript types
npx mcporter codegen types server-name

# Generate TypeScript client
npx mcporter codegen client server-name
```

## OAuth Login

```bash
npx mcporter login server-name
```

## Config Management

```bash
npx mcporter config list
npx mcporter config add server-name --stdio "command args"
npx mcporter config remove server-name
```

## Daemon Mode

```bash
# Keep connections alive for faster subsequent calls
npx mcporter daemon start
npx mcporter daemon stop
```

## MCP Registry Discovery

The [MCP Registry](https://registry.modelcontextprotocol.io) provides a public API for discovering MCP servers. Use it to find servers before configuring them locally:

```bash
# Search for servers by name
curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=slack"

# Get latest version of a specific server
curl "https://registry.modelcontextprotocol.io/v0.1/servers/io.github.username%2Fserver/versions/latest"
```

This complements mcporter's local discovery — the registry finds _what exists_, mcporter manages _what's configured_.
