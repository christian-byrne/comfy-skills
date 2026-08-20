# Agent-Native Operability Checks

An agent driving a web app does not see your UI. It sees one of three things:

1. **the accessibility tree** — Playwright, `agent-browser`, and Claude's computer-use snapshots
   navigate by `role` + accessible `name`
2. **serialized DOM text** — `page-agent` and similar read the DOM as compact text and act on it
   (DOM-as-text serialization)
3. **pixels** — vision fallback, the slowest and least reliable path, and the only one left when 1 and 2
   are empty

Modes 2 and 3 are often lumped together as "browser automation", but they have opposite properties and
only one of them is designable: the **accessibility tree** is structured, cheap, and something you build
toward, while **screenshots** are unstructured, expensive, and cannot be designed for beyond "be visible
at rest." Design for 1, build for 2, and treat 3 as the fallback you only influence indirectly. 

An element is **agent-legible** only when it survives all three at once: it exists in markup, it has an
accessible name and state, and it is visible at rest. Most component failures fail exactly one mode,
which is why they survive review — the thing works when a human checks it the way humans check things.

A second rule follows from how agents act: they snapshot, decide, then act. **Anything that changes
between the read and the act is a correctness hazard**, not a polish item — a carousel, a cycling label,
a late-resolving feature flag, a list that re-sorts. An agent can act on the wrong element and report
success.

For the author-facing version of all of this — what to build, component by component — see
`component-guidance.md`.

This overlaps human accessibility but is not the same audit. WCAG asks "can a screen-reader user
perceive this". This asks "can a program identify this control, know its state, and confirm its action
completed". A dedicated WCAG scanner covers that side; do not duplicate it — cite it.

## §1. Accessible name and role on every interactive thing

- icon-only buttons with no `aria-label` / visible text → **blocking**. In an accessibility snapshot the
  control appears as `button` with no name; an agent has nothing to target and no way to distinguish it
  from the four other unnamed buttons in the toolbar.
- `<div>` / `<span>` with a click handler and no `role`/`tabindex` → invisible as a control in both the
  tree and most DOM serializers
- duplicate accessible names in one view ("Edit", "Edit", "Edit") → ambiguous target; an agent picks the
  first and silently does the wrong thing. Disambiguate with context in the name, not with DOM position.
- native element replaced by a styled `div` where `<button>`/`<a>`/`<select>`/`<dialog>` existed
- form controls with a placeholder but no `<label>` / `aria-label`
- the accessible name coming from a CSS pseudo-element or a background image

## §2. State an agent can read

An agent needs to know what happened, not just what to click.

- toggles/checkboxes/tabs without `aria-pressed` / `aria-checked` / `aria-selected` / `aria-expanded` —
  visual-only state (a color change or a Tailwind class) is unreadable
- loading state with no `aria-busy` and no status text → the agent cannot tell "still working" from
  "finished, nothing happened", and screenshot-based confirmation is not an assertion
- results/errors that appear without an `aria-live` region or a role=`status`/`alert` → never announced,
  and easy for an agent to miss between snapshots
- disabled state via `pointer-events: none` or a CSS class instead of the `disabled` attribute /
  `aria-disabled`
- modals without `role="dialog"` + `aria-modal` and without focus management → an agent keeps operating
  the page behind the overlay

## §3. Stable anchors

Prefer, in order: role + accessible name → landmark/heading structure → stable semantic attribute.

- selectors keyed to Tailwind classes, generated hashes, or DOM position break on every refactor
- `data-testid` is a **test** anchor, not an agent affordance — it does not appear in the accessibility
  tree. Adding one does not make a control agent-operable. (It is still worth having for e2e; just do not
  file it as the fix for a naming gap.)
- `toMatchAriaSnapshot()` on the main views turns "agents can still navigate this" into a CI assertion —
  the cheapest available regression guard on agent operability, and it fails loudly on refactors
- keyboard reachability: every action reachable by Tab/Enter, visible focus, no focus traps. Hover-only
  affordances (menus that open on `mouseenter` only) are unreachable for an agent driving via the tree.

## §4. The canvas / opaque-widget gap

A `<canvas>` is one opaque node with no children. Everything drawn inside it — nodes, links, charts,
handles, a whole graph editor — is invisible to the accessibility tree and to DOM serialization. Same for
WebGL surfaces, custom-rendered virtual lists that only mount visible rows, and content inside closed
shadow DOM.

When the diff touches such a surface, the finding is not "add ARIA to the canvas" — it is:

- is there an explicit accessibility bridge (offscreen DOM mirror, ARIA-annotated fallback elements,
  or a documented programmatic API for the same operations)?
- if not, say so plainly and route agent workflows to §5 instead of pretending the UI is operable.
  A node-graph editor is the standing example: its DOM overlays are agent-testable and its canvas is not,
  so natural-language UI testing has to be scoped to the overlays.

## §5. The programmatic path (often the real answer)

The best agent affordance is frequently "do not use the UI".

- is there a documented CLI, API, or MCP server that performs the same operations, and does the product
  **point agents at it**? `llms.txt` and `AGENTS.md` are where that pointer belongs.
- is the OpenAPI/GraphQL schema published, current, and reachable without a login wall?
- can a headless agent authenticate at all — token auth, or only an interactive OAuth/SSO redirect and a
  CAPTCHA? An MCP or API surface an agent cannot get a credential for is not a path.
- CORS and rate limits: does the documented path work from the environment agents actually run in?
- error messages: does a failure return something actionable (`missing field: prompt.model`) or a generic
  500 / a toast with no text in the response body?
- idempotency: an agent retries. Are the write endpoints safe to call twice?
- MCP-first is a legitimate architecture, not a bolt-on — one server can back the connector, the SDK,
  the chat adapters, and the dashboard (the MCP-first architecture pattern). When a product is adding agent
  support, that is the question worth raising in review.

## §6. Findings that are not findings

- WCAG violations with no agent consequence → route to a WCAG scanner, do not restate
- ARIA piled onto an element that should have been native (first rule of ARIA: don't)
- "expose an MCP server" as a drive-by suggestion on an unrelated diff — genuine, but it is a roadmap
  conversation, not a review comment
- speculative agent workflows nobody asked for
