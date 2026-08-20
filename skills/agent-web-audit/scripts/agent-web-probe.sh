#!/usr/bin/env bash
# agent-web-probe.sh — Static fingerprint of a web frontend's agent-readiness surface.
#
# Reports what the agent-web-audit lenses need before they can judge anything:
# render mode, where <head> is assembled, which machine-readable descriptors exist,
# and how the UI exposes itself to accessibility-tree navigation.
#
# It reports presence and counts only. It does not score, and a count is not a finding —
# read the output, then read the code it points at.
#
# Usage:
#   bash agent-web-probe.sh [repo-root]   # defaults to $PWD

set -euo pipefail

ROOT="${1:-$PWD}"

if [[ ! -d "$ROOT" ]]; then
  echo "agent-web-probe: not a directory: $ROOT" >&2
  exit 2
fi

cd "$ROOT"

PRUNE=(
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=build
  --exclude-dir=.next --exclude-dir=.nuxt --exclude-dir=.output --exclude-dir=.svelte-kit
  --exclude-dir=coverage --exclude-dir=vendor --exclude-dir=.venv --exclude-dir=venv
  --exclude-dir=target --exclude-dir=__pycache__ --exclude-dir=.turbo --exclude-dir=.cache
)

# Count files matching a pattern. No matches is 0, not a failure — grep exits 1 on no match
# and `set -o pipefail` would otherwise abort the whole probe on the first empty result.
hits() {
  { command grep -RIl --binary-files=without-match "${PRUNE[@]}" -e "$1" . 2>/dev/null || true; } |
    wc -l | tr -d ' '
}

# List up to N paths matching a pattern.
paths() {
  local pattern="$1" limit="${2:-5}"
  { command grep -RIl --binary-files=without-match "${PRUNE[@]}" -e "$pattern" . 2>/dev/null || true; } |
    head -n "$limit"
}

# Locate a descriptor file by name, ignoring vendored copies.
locate() {
  find . -name "$1" -not -path "*/node_modules/*" -not -path "*/.git/*" \
    -not -path "*/dist/*" -not -path "*/.next/*" 2>/dev/null | head -n 5
}

section() { printf '\n## %s\n\n' "$1"; }

# Literal backtick, so markdown code spans survive shellcheck's single-quote rule.
BT='`'

# Print "found" lines for a descriptor, or a marked absence.
report_paths() {
  local label="$1" found="$2"
  if [[ -n "$found" ]]; then
    printf -- '- %s: %s%s%s\n' "$label" "$BT" "$(echo "$found" | tr '\n' ' ' | sed 's/ *$//')" "$BT"
  else
    printf -- '- %s: **absent**\n' "$label"
  fi
}

printf '# agent-web probe — %s\n' "$ROOT"

section 'Machine-readable descriptors'
report_paths 'robots.txt' "$(locate 'robots.txt')"
report_paths 'llms.txt' "$(locate 'llms.txt')"
report_paths 'llms-full.txt' "$(locate 'llms-full.txt')"
report_paths 'sitemap' "$(locate 'sitemap*.xml'; locate 'sitemap*.ts'; locate 'sitemap*.js')"
report_paths 'AGENTS.md' "$(locate 'AGENTS.md')"
report_paths 'OpenAPI' "$(locate 'openapi*.json'; locate 'openapi*.yaml')"
printf -- '- generated-descriptor signals (sitemap/robots emitted by code): %s file(s)\n' \
  "$(hits 'sitemap\|robots')"

section 'Render mode'
printf -- '- framework deps in package.json:\n'
if [[ -f package.json ]]; then
  command grep -oE '"(next|nuxt|astro|@remix-run/[a-z]+|@sveltejs/kit|gatsby|vue|react|svelte|solid-js|vite|@vitejs/plugin-[a-z]+)"' \
    package.json 2>/dev/null | sort -u | sed 's/^/  - /' || echo '  - (none matched)'
else
  echo '  - (no package.json at root — check workspace packages)'
fi
printf -- '- SSR/SSG/prerender config mentions: %s file(s)\n' "$(hits 'ssr:\|prerender\|getStaticProps\|getServerSideProps\|output: *.static\|renderToString')"
printf -- '- client-only / SPA-fallback signals: %s file(s)\n' "$(hits 'client-only\|ClientOnly\|createApp(\|ReactDOM.createRoot\|hydrateRoot')"
printf -- '- noindex occurrences: %s file(s)\n' "$(hits 'noindex')"
printf -- '- rel="canonical" occurrences: %s file(s)\n' "$(hits 'rel="canonical"\|rel=.canonical')"

section 'Head / metadata assembly'
printf -- '- head-management calls: %s file(s)\n' "$(hits 'useHead(\|useSeoMeta(\|<Head>\|Helmet\|generateMetadata\|defineMetadata\|document.title')"
paths 'useHead(\|useSeoMeta(\|<Head>\|Helmet\|generateMetadata' 5 | sed 's/^/  - /'
printf -- '- Open Graph / twitter card mentions: %s file(s)\n' "$(hits 'og:title\|og:description\|twitter:card')"

section 'Structured data'
printf -- '- JSON-LD blocks: %s file(s)\n' "$(hits 'application/ld+json')"
paths 'application/ld+json' 5 | sed 's/^/  - /'
printf -- '- schema.org references: %s file(s)\n' "$(hits 'schema.org')"

section 'Accessibility-tree surface'
printf -- '- aria-label / aria-labelledby: %s file(s)\n' "$(hits 'aria-label')"
printf -- '- explicit role= attributes: %s file(s)\n' "$(hits 'role="\|role=.')"
printf -- '- aria state attributes (pressed/checked/expanded/selected/busy): %s file(s)\n' \
  "$(hits 'aria-pressed\|aria-checked\|aria-expanded\|aria-selected\|aria-busy')"
printf -- '- aria-live / role=status|alert regions: %s file(s)\n' "$(hits 'aria-live\|role="status"\|role="alert"')"
printf -- '- data-testid anchors: %s file(s)  (test anchors, NOT agent affordances)\n' "$(hits 'data-testid')"
printf -- '- getByRole in tests: %s file(s)\n' "$(hits 'getByRole')"
printf -- '- toMatchAriaSnapshot assertions: %s file(s)\n' "$(hits 'toMatchAriaSnapshot')"

section 'Opaque surfaces'
printf -- '- <canvas> usage: %s file(s)\n' "$(hits '<canvas')"
paths '<canvas' 5 | sed 's/^/  - /'
printf -- '- WebGL / three.js: %s file(s)\n' "$(hits 'getContext(.webgl\|three')"
printf -- '- closed shadow DOM: %s file(s)\n' "$(hits 'mode: *.closed')"

section 'Handoff surface (path 2)'
printf -- '- clipboard / copy affordances: %s file(s)\n' "$(hits 'navigator.clipboard\|useClipboard\|copyToClipboard\|execCommand(.copy')"
printf -- '- markdown export or .md route: %s file(s)\n' "$(hits 'text/markdown\|\.md?raw\|toMarkdown\|as-markdown')"
printf -- '- user-select: none (blocks copying): %s file(s)\n' "$(hits 'user-select: *none\|select-none')"
printf -- '- CSS pseudo-element content (meaning a copy loses): %s file(s)\n' "$(hits ':: *before *{[^}]*content:\|::after')"
printf -- '- virtualization: %s file(s)\n' "$(hits 'virtual-scroll\|useVirtual\|VirtualList\|react-window\|tanstack/virtual\|vue-virtual')"
printf -- '- stepper / wizard components: %s file(s)\n' "$(hits 'Stepper\|stepIndex\|currentStep\|wizard')"
printf -- '- print stylesheet: %s file(s)\n' "$(hits '@media print')"

section 'Programmatic path'
printf -- '- MCP server/tool definitions: %s file(s)\n' "$(hits 'modelcontextprotocol\|mcpServers\|@mcp\|McpServer')"
bin_count=0
if [[ -f package.json ]]; then
  bin_count="$(command grep -c '"bin"' package.json 2>/dev/null || true)"
  [[ -n "$bin_count" ]] || bin_count=0
fi
printf -- '- CLI entrypoints (package.json bin): %s\n' "$bin_count"
printf -- '- CORS configuration: %s file(s)\n' "$(hits 'Access-Control-Allow-Origin\|cors(')"
printf -- '- rate-limit configuration: %s file(s)\n' "$(hits 'rateLimit\|rate_limit\|X-RateLimit')"

printf '\n_Presence and counts only. Zero can mean "not applicable" as easily as "missing" — confirm against the code before filing anything._\n'
