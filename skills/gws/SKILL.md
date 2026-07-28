---
name: gws
description: 'Execute Google Workspace operations via the gws CLI — send/read emails, manage calendar, read/write spreadsheets, access Drive, edit Docs. Structured JSON output, helper commands (+send, +triage, +agenda, +read, +append). Use when running gws commands, writing gws CLI scripts, or directly interacting with Google APIs from the terminal.'
interaction: hybrid
type: leaf
synergies:
  requires: []
  domain: [google, email, calendar, productivity, cli]
---

# Google Workspace CLI (gws)

One CLI for all of Google Workspace — Drive, Gmail, Calendar, Sheets, Docs, Chat, Admin, and more. Built for humans and AI agents. All output is structured JSON.

**Key advantage over the Python SDK approach:** No boilerplate, no `google-api-python-client` setup, no pickle token management. `gws` handles auth, pagination, schema discovery, and structured output natively.

> **Not officially supported by Google.** Apache-2.0, active development, pre-v1.0. Expect breaking changes.

## Prerequisites

1. **Node.js 18+** (for npm install) or download a pre-built binary
2. **A Google Cloud project** with OAuth credentials
3. **A Google account** with Workspace access

## Install

```bash
# Preferred: pre-built binary
# https://github.com/googleworkspace/cli/releases

# Or via npm
npm install -g @googleworkspace/cli

# Or via Homebrew (macOS/Linux)
brew install googleworkspace-cli

# Or build from source
cargo install --git https://github.com/googleworkspace/cli --locked
```

**Verify:**

```bash
gws --version
```

If `gws` is not found after npm install, ensure your npm global bin is in PATH:

```bash
export PATH="$PATH:$(npm config get prefix)/bin"
```

## Authentication

### Automated setup (requires `gcloud` CLI)

```bash
gws auth setup     # Creates GCP project, enables APIs, logs you in
gws auth login     # Subsequent logins
```

### Manual setup (no `gcloud`)

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials
2. Create OAuth 2.0 Client ID (Desktop app)
3. Download `client_secret.json` to `~/.config/gws/client_secret.json`
4. Enable APIs you need: Gmail, Calendar, Drive, Sheets, Docs
5. Add yourself as a test user in OAuth consent screen
6. Run `gws auth login`

### Scope limiting (important for unverified apps)

Unverified apps are limited to ~25 OAuth scopes. Select only what you need:

```bash
# Recommended: pick specific services
gws auth login -s drive,gmail,sheets,calendar,docs

# NOT recommended for unverified apps:
# gws auth login  (uses all 85+ scopes — will fail)
```

### Service account (server-to-server)

```bash
export GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE=/path/to/service-account.json
gws drive files list
```

### Pre-obtained token

```bash
export GOOGLE_WORKSPACE_CLI_TOKEN=$(gcloud auth print-access-token)
```

Credentials are encrypted at rest (AES-256-GCM) with the key stored in your OS keyring.

## Core Commands

`gws` discovers API methods dynamically from Google's Discovery Service — no static command list. The pattern is:

```bash
gws <service> <resource> <method> [--params '{}'] [--json '{}']
```

### Drive

```bash
# List files
gws drive files list --params '{"pageSize": 10}'

# Search for files
gws drive files list --params '{"q": "name contains '\''report'\'' and mimeType='\''application/pdf'\''", "pageSize": 5}'

# Download a file
gws drive files get --params '{"fileId": "FILE_ID"}' --download ./output.pdf

# Upload a file
gws drive +upload ./report.pdf --name "Q1 Report"
```

### Gmail

```bash
# Triage inbox (unread summary)
gws gmail +triage

# Send an email
gws gmail +send --to alice@example.com --subject "Hello" --body "Hi there"

# Reply to a message
gws gmail +reply --message-id MESSAGE_ID --body "Thanks!"

# Reply all
gws gmail +reply-all --message-id MESSAGE_ID --body "Acknowledged"

# Forward a message
gws gmail +forward --message-id MESSAGE_ID --to bob@example.com

# Search emails
gws gmail users messages list --params '{"q": "from:boss@company.com after:2024/01/01", "maxResults": 10}'

# Read a specific message
gws gmail users messages get --params '{"id": "MESSAGE_ID"}'

# Watch for new emails (streaming)
gws gmail +watch
```

### Calendar

```bash
# Today's agenda (uses your Google account timezone)
gws calendar +agenda

# Agenda in a specific timezone
gws calendar +agenda --today --timezone America/New_York

# Create an event
gws calendar +insert --summary "Team sync" --start "2026-04-10T14:00:00" --end "2026-04-10T15:00:00"

# List upcoming events
gws calendar events list --params '{"calendarId": "primary", "timeMin": "2026-04-08T00:00:00Z", "maxResults": 10, "singleEvents": true, "orderBy": "startTime"}'
```

### Sheets

```bash
# Read values from a spreadsheet
gws sheets +read --spreadsheet SPREADSHEET_ID --range "Sheet1!A1:D10"

# Append a row
gws sheets +append --spreadsheet SPREADSHEET_ID --values "Alice,95"

# Create a spreadsheet
gws sheets spreadsheets create --json '{"properties": {"title": "Q1 Budget"}}'
```

### Docs

```bash
# Append text to a document
gws docs +write --document DOC_ID --text "New section content"

# Read a document
gws docs documents get --params '{"documentId": "DOC_ID"}'
```

## Workflow Helpers

Higher-level commands for common agent workflows:

```bash
# Morning standup summary (today's meetings + open tasks)
gws workflow +standup-report

# Prepare for your next meeting (agenda, attendees, linked docs)
gws workflow +meeting-prep

# Convert an email to a Google Tasks entry
gws workflow +email-to-task

# Weekly digest (meetings + unread count)
gws workflow +weekly-digest
```

## Introspection

```bash
# See all available services
gws --help

# See methods for a service (Discovery + helpers)
gws drive --help
gws gmail --help

# Inspect request/response schema for any method
gws schema drive.files.list

# Preview a request without executing
gws drive files list --params '{"pageSize": 5}' --dry-run

# Stream paginated results as NDJSON
gws drive files list --params '{"pageSize": 100}' --page-all | jq -r '.files[].name'
```

## Agent Recipes

### Read a Google Doc into agent context

```bash
# Get doc content as JSON
DOC=$(gws docs documents get --params '{"documentId": "DOC_ID"}')
echo "$DOC" | jq '.body.content'
```

### Search Drive and read results

```bash
# Find recent spreadsheets
gws drive files list --params '{"q": "mimeType='\''application/vnd.google-apps.spreadsheet'\''", "pageSize": 5, "orderBy": "modifiedTime desc"}'
```

### Email triage → create tasks

```bash
# Show unread, then convert urgent ones to tasks
gws gmail +triage
gws workflow +email-to-task --message-id MSG_ID
```

### Feed spreadsheet data into agent

```bash
# Read a range and pipe to processing
gws sheets +read --spreadsheet SHEET_ID --range "Data!A1:Z100" | jq '.values'
```

## Exit Codes

| Code | Meaning          | Action                              |
| ---- | ---------------- | ----------------------------------- |
| `0`  | Success          | —                                   |
| `1`  | API error        | Check the JSON error response       |
| `2`  | Auth error       | Run `gws auth login` or check creds |
| `3`  | Validation error | Check arguments / flags             |
| `4`  | Discovery error  | Network issue or unknown service    |
| `5`  | Internal error   | Report upstream                     |

## Environment Variables

| Variable                                | Description                                          |
| --------------------------------------- | ---------------------------------------------------- |
| `GOOGLE_WORKSPACE_CLI_TOKEN`            | Pre-obtained OAuth2 access token                     |
| `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` | Path to OAuth credentials JSON                       |
| `GOOGLE_WORKSPACE_CLI_CONFIG_DIR`       | Override config directory (default: `~/.config/gws`) |
| `GOOGLE_WORKSPACE_CLI_LOG`              | Log level for stderr (e.g., `gws=debug`)             |

## Troubleshooting

- **"Access blocked" / 403:** Add yourself as a test user in OAuth consent screen → Test users → Add users
- **"Google hasn't verified this app":** Click Advanced → Go to app (unsafe). Safe for personal use.
- **Too many scopes:** Use `gws auth login -s drive,gmail,sheets` instead of all scopes
- **API not enabled:** Follow the `enable_url` in the error JSON, click Enable, wait 10s, retry
- **`gcloud` not found:** Use manual OAuth setup instead of `gws auth setup`

## Rules

- **Never send emails or create events without explicit user confirmation**
- Store credentials in `~/.config/gws/` — never commit to repos
- Use `-s` flag with `auth login` to limit scopes to what you actually need
- All output is JSON — pipe through `jq` for extraction
- Pre-v1.0: pin to a specific version in CI/automation scripts
