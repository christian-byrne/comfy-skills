---
name: agent-browser
description: Browser automation for visual QA using Vercel's agent-browser CLI. Compact accessibility snapshots, ref-based element interaction, screenshot capture. Use when verifying UI changes, testing interactions, or running visual QA on a running dev server.
type: leaf
---

# Agent-Browser

Lightweight browser automation via [Vercel's agent-browser](https://github.com/vercel-labs/agent-browser) CLI. Uses compact accessibility tree snapshots with element refs (`@e1`, `@e2`) instead of full DOM dumps — ~90% fewer tokens than Playwright MCP.

## When to Use

- **Visual QA** — verify UI changes render correctly on a running dev server
- **Interaction testing** — click buttons, fill forms, verify state changes
- **Console error detection** — catch JS errors, failed requests, Vue warnings
- **Screenshot capture** — document visual state for reports or PR descriptions
- **Design verification** — compare rendered output against design standards

## When NOT to Use

- **Unit/integration tests** — use Vitest
- **E2E test suites** — use Playwright directly (more assertions, parallel browsers)
- **Complex network mocking** — use Playwright's full API
- **Production debugging** — agent-browser is for local dev servers

## Prerequisites

```bash
# Install (one-time)
npm install -g agent-browser
agent-browser install  # Downloads Chromium

# Verify
agent-browser --version
```

## Core Workflow

### 1. Open & Snapshot

```bash
# Open the dev server
agent-browser open http://localhost:5173

# Get interactive elements as compact refs
agent-browser snapshot -i
# Output:
# - heading "ComfyUI" [ref=e1]
# - button "New Workflow" [ref=e2]
# - link "Settings" [ref=e3]
```

### 2. Interact via Refs

```bash
# Click an element
agent-browser click @e2

# Fill an input
agent-browser fill @e3 "my-workflow"

# Hover (useful for tooltips, dropdowns)
agent-browser hover @e4

# Select from dropdown
agent-browser select @e5 "option-value"
```

### 3. Verify & Capture

```bash
# Screenshot current state
agent-browser screenshot screenshot-after-click.png

# Check console for errors
agent-browser console

# Get page title (quick sanity check)
agent-browser get title

# Get current URL (verify navigation)
agent-browser get url
```

### 4. Multi-Page Verification

```bash
# Navigate to another route
agent-browser navigate http://localhost:5173/settings

# Fresh snapshot of new page
agent-browser snapshot -i

# Screenshot for comparison
agent-browser screenshot screenshot-settings.png
```

### 5. Cleanup

```bash
agent-browser close
```

## Sessions (Parallel Isolation)

Use named sessions when testing multiple states simultaneously:

```bash
# Session 1: default state
agent-browser open http://localhost:5173 --session default-state
agent-browser screenshot default.png --session default-state

# Session 2: after changes
agent-browser open http://localhost:5173 --session modified-state
agent-browser click @e2 --session modified-state
agent-browser screenshot modified.png --session modified-state

# Cleanup both
agent-browser close --session default-state
agent-browser close --session modified-state
```

## Common Patterns

### Quick Page Health Check

```bash
agent-browser open "$URL"
agent-browser console          # Any JS errors?
agent-browser snapshot -i      # Page structure intact?
agent-browser screenshot /tmp/health.png
agent-browser close
```

### Verify a Button Click Produces Expected Result

```bash
agent-browser open "$URL"
agent-browser snapshot -i                    # Find the button ref
agent-browser click @e5                      # Click it
agent-browser snapshot -i                    # Check what changed
agent-browser screenshot /tmp/after-click.png
agent-browser close
```

### Test Form Submission

```bash
agent-browser open "$URL"
agent-browser snapshot -i
agent-browser fill @e3 "test@example.com"
agent-browser fill @e4 "Test User"
agent-browser click @e5                      # Submit
agent-browser snapshot -i                    # Verify success state
agent-browser close
```

## Where This Fits

- Use it as a lightweight alternative to a full Playwright suite for quick visual checks
- Run it as an automated pre-check before manual QA
- Use it to verify rendered output against your own design standards

## Tips

- **Re-snapshot after interactions** — refs change when the page updates
- **Use `snapshot -i`** (interactive only) — skips decorative elements, fewer tokens
- **Screenshots are your evidence** — always capture before/after for PR descriptions
- **Console output catches Vue warnings** — not just errors
- **Sessions persist** — always `close` when done to free resources
