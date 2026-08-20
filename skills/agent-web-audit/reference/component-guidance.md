# Component Guidance (author-facing)

The rest of this skill is written for a reviewer: what to file, and what not to. This file is the
other direction — what to build, per component, so the review finds nothing. Hand it to a designer or
give it to an agent implementing UI.

Adapted from a designer's agent-friendly UX reference (19 Aug 2026), with corrections noted inline
where the original was too generous. Sources for the underlying mechanics: `agent-native-checks.md`.

## The three modes, and the conjunctive test

An agent reads a page in one of three ways, in rough order of how common they are:

1. **Text fetch** — HTML converted to markdown (`WebFetch`, `curl`). No JS runs, nothing is hovered,
   nothing is clicked. Whatever the raw markup says is all there is.
2. **Accessibility tree** — browser-driving agents read the same tree a screen reader does: roles,
   names, states. They can click and type, but they find things by **label, not by position or colour**.
3. **Screenshots** — vision models, sampled at moments. Anything transient or hover-gated is missed.

> An element is **agent-legible** when it survives all three: it exists in markup, it has an accessible
> name and state, and it is visible at rest.

That conjunction is the whole test. Most component failures are a failure of exactly one mode, which is
why they survive casual review — the thing works when a human checks it the way humans check things.

**The principle, once:** never let information exist only in a place that requires being present at the
right moment, hovering, or inferring from appearance. Components are rarely the problem. Where the
information lives is.

**The corollary that matters most:** a UI that changes between the agent's read and its act is a
correctness hazard, not an inconvenience. An agent snapshots, decides, then acts — anything that moves
in between (a carousel, a cycling label, a late-resolving flag, a row that re-sorts) can make it act on
the wrong element. Treat "moving target" as a bug class, not a polish item.

## Fine as-is

| Component                                                               | Why it works                                                 |
| ----------------------------------------------------------------------- | ------------------------------------------------------------ |
| Headings, lists, tables, definition lists                               | Structure **is** the agent interface. This is the good case. |
| Buttons and links with real text                                        | Name and role come free                                      |
| Status pills whose text says the state                                  | "Ready", "Stopped" — never colour alone                      |
| Disclosure where content stays in the DOM **and is not `display:none`** | See the caveat below                                         |

## Fine with care

| Component                    | The care it needs                                                                                                                                                                                                                                                               |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tooltips / popovers          | Fine as **redundant** detail; never the sole carrier of state or instructions. Wire the text with `aria-describedby` so it exists in the tree unhovered. Visible state stays on the element; the remedy may live in the tooltip.                                                |
| Icon-only buttons            | `aria-label` says what it **does** — "Copy page as markdown", not "copy icon"                                                                                                                                                                                                   |
| Tabs                         | Keep unselected panels in the DOM, or make each tab a real URL. The URL is the better answer: it is also citable.                                                                                                                                                               |
| Hover-revealed row actions   | Prefer visible at rest. If hidden, hide with `opacity` or offscreen positioning — `display:none` and `visibility:hidden` remove the element from the accessibility tree too, so it fails mode 2 as well as mode 3, not just mode 3.                                             |
| Drag-and-drop                | Always pair with a plain file input or button ("Choose a file"). The drop gesture is un-performable for most agents.                                                                                                                                                            |
| Truncation with ellipsis     | Keep the full value in the markup (`title`, `aria-label`), not only in the shortened render                                                                                                                                                                                     |
| Modals and dialogs           | They enter the DOM when opened, which is the easy part. They need `role="dialog"` + `aria-modal` **and** focus management — without it an agent keeps happily operating the page behind the overlay.                                                                            |
| Skeletons and loading states | Only safe with `aria-busy` or a status region. An agent cannot otherwise distinguish "still loading" from "loaded, empty" — a screenshot of a skeleton looks like content, and a text fetch never sees the resolved state at all.                                               |
| Virtualized long lists       | Only mounted rows exist. A fetch, a copy and a screenshot all capture the window and none of them signal that they truncated. Keep the virtualization — it is usually a real perf requirement — and add an escape: a paged route, `?all=1`, or an export.                       |
| Steppers / wizards           | The worst structure on this list: stateful, unaddressable, unmounts answered steps, and changes under an agent that re-reads. Give each step a URL, and a review step that renders every answer at once.                                                                        |
| Accordions / disclosure      | "Collapsed content is still in the DOM" is not a safe default. `v-if` and lazy panels remove it outright; `display:none` keeps it in the DOM but drops it from the accessibility tree, and HTML-to-markdown converters disagree about whether to keep it. Verify per component. |

## Avoid, or provide a text twin

| Pattern                                                 | Why it breaks                                                                                                                                                                                                            |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Toasts as the only confirmation                         | Transient. The result must also persist inline — "Key created" stays on the page, not just for 3s.                                                                                                                       |
| Auto-advancing anything                                 | Carousels, cycling labels. Agents sample; moving targets get missed, and can change state between read and click.                                                                                                        |
| Hover-only tooltips carrying unique content             | Invisible in modes 1 and 3                                                                                                                                                                                               |
| Meaning carried by colour, position, or proximity alone | "the red one", "the card next to it". Every state needs words somewhere in the markup.                                                                                                                                   |
| Canvas / WebGL content, and image-of-text               | Opaque to modes 1 and 2. Charts need a data table or summary twin.                                                                                                                                                       |
| Placeholder-as-label inputs                             | The label vanishes on type; agents and humans both lose the field's name                                                                                                                                                 |
| Infinite scroll as the only pagination                  | A text fetch gets one window. Offer real paged URLs or a "view all" route.                                                                                                                                               |
| Content gated on arbitrary JS timing                    | A feature-flag resolve with a multi-second fallback timeout gates the UI at page scale. Real instance measured in a production Nuxt app: a feature-flag composable resolved on the analytics SDK's callback *or* a 2500ms `setTimeout`, whichever landed first, so gated UI could take 2.5s to settle. |
| Duplicate accessible names in one view                  | "Edit", "Edit", "Edit". The agent picks the first and silently does the wrong thing.                                                                                                                                     |

## Page-level habits

These outrank any component choice.

- **Stable deep links.** Every list, filter state, and detail view addressable by URL. An agent — and a
  teammate — can then cite it and return to it. This is the single highest-leverage habit on the list.
- **One aggregate route as well.** Addressability and one-fetch-gets-everything pull against each
  other and are both right. The synthesis is a canonical URL per unit **plus** an aggregate view
  (`?all=1`, an export, a print stylesheet) — not "put everything on one page", which destroys the
  addressability.
- **Export affordances.** Copy as markdown, copy for agent, a `.md` twin of the route, copy controls on
  ids and error codes. On an authenticated surface a person ferrying the page into a prompt is the main
  way an agent ever sees it, so this outranks most of the component table above. See
  `handoff-checks.md`.
- **State in text.** "3 builds, 1 deployment ready" as words is worth more than any dashboard visual.
- **Confirm completion, not just initiation.** A live region or status role that says the action landed.
  A screenshot is not an assertion.
- **Idempotent writes.** Agents retry. A double-submitted create is the agent-era version of the
  double-clicked button.
- **Errors an agent can act on.** `missing field: prompt.model`, not a generic 500 and a toast with
  nothing in the response body.
- **Markdown mirrors + `llms.txt`** for docs and public pages. For an authed console the agent surface
  is the CLI/API/MCP, not DOM scraping — say so in `llms.txt` rather than pretending the UI is the path.

## The test

`curl` the page and read the result. If the answer to "what is this page and what can I do here" is not
in that text, an agent does not know either.

Measured example of failing it: a production `ssr: false` dashboard returned ~604KB of HTML containing
**zero characters of visible text** once scripts and tags were stripped.

## Keeping it true

A guidance document with no enforcement decays into a document nobody opens. The enforcement for this
one is `toMatchAriaSnapshot()` on the main views: it turns "an agent can still navigate this" into a CI
assertion that fails loudly on the refactor that breaks it. Everything above is advice until that exists.
