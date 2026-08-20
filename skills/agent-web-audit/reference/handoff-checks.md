# Handoff Checks — the human-ferried path

The other paths assume a machine arrives under its own power. This one assumes a **person** is moving
the page into a machine: selecting, copying, screenshotting, pasting into a prompt. Different actor,
different test.

> Not "can an agent read this page" but **"how many actions does it take a person to get this page into
> a prompt, and does it survive the trip."**

This is the path everyone actually uses and nobody designs for. It is also the **only** path that works
on an authenticated surface, where a fetcher gets a login wall and a headless agent cannot get a
credential. On a login-walled console this outranks everything except a real API.

## §1. Export affordances

The whole path collapses to one question: is there a button.

- **"Copy as Markdown"** on any page whose content is worth quoting — a doc, a run log, an error, a
  config, a table of results. One click beats a selection drag every time, and it produces clean
  markdown rather than whatever the clipboard negotiated.
- **"Copy for agent" / "Copy prompt"** where the useful artifact is not the page but a
  ready-to-paste instruction: the failing command plus its output, the resource id plus the CLI
  invocation that acts on it, the error plus the file it came from. This is the highest-value version
  and the rarest.
- **A `.md` twin of the route** (`/runs/123` → `/runs/123.md`). Docs sites do this routinely; app
  surfaces almost never do, though an authed `.md` route behind the same session cookie is no harder
  than the HTML one and is trivially pasteable.
- **Copy on the primitives**, not only the page: ids, keys, endpoints, error codes, log lines, command
  snippets. A resource id a person has to retype by eye is a transcription bug waiting to happen.
- **An export or print view** for anything paginated or virtualized. See §3.

When reviewing, the finding is rarely "add a copy button" in the abstract. It is: _this specific page is
the one people paste into agents, and getting its content out currently takes a drag-select across a
virtualized table._

## §2. Does the content survive the trip

A copy affordance that yields mangled text is worse than none, because the damage is silent.

- `user-select: none` on content — legitimate on chrome and drag handles, a bug on anything readable
- meaning carried in CSS pseudo-element content (`::before { content: "Required" }`) — invisible to
  both a copy and the accessibility tree
- tables that copy as a single run-on line rather than rows and columns; a real `<table>` survives, a
  grid of `<div>`s does not
- values shown truncated where only the ellipsis-ed form is in the DOM (see `component-guidance.md`)
- icon-only status with no text twin — "Ready" pastes, a green dot does not
- content in `<canvas>` or an image of text — nothing to select at all
- numbers formatted for display only, where the underlying precision is gone

## §3. One addressable unit, and an escape from the window

Two rules that pull against each other and are both right.

**Every coherent unit of information gets its own URL.** A list, a filter state, a detail view, a
wizard step. An agent and a teammate can then cite it, return to it, and diff it. This is the highest
leverage habit in the whole skill and the one most often missing.

**And there is a way to get the whole thing in one fetch.** A person ferrying context does not want to
paste eleven URLs. An aggregate view, a `?all=1`, an export endpoint, a print stylesheet.

The synthesis is _not_ "put everything on one page" — that destroys addressability. It is: canonical
URL per unit, plus one aggregate route that concatenates them.

Where this breaks today:

| Pattern            | Why the ferry fails                                                                                                          | Escape                                                                                                                     |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Virtualized lists  | Only mounted rows exist in the DOM. A copy captures the window, not the list, and gives no sign that it truncated.           | `?all=1`, an export, or a paged route. Do not ask the team to drop virtualization — it is usually there for a real reason. |
| Infinite scroll    | Same, plus no stable address for "page 2"                                                                                    | Real paged URLs                                                                                                            |
| Steppers / wizards | Each step's answers live in component state; nothing but the current step is on the page, and there is no address for step 3 | A URL per step, and a review step that shows every answer at once                                                          |
| Tabs               | Unselected panels often unmounted                                                                                            | A URL per tab, or keep panels mounted                                                                                      |
| Modals             | Content is unreachable without the interaction that opens it                                                                 | A route for anything worth citing                                                                                          |
| Collapsed sections | `v-if` removes it; `display:none` hides it from the tree                                                                     | `v-show`, or expand-all                                                                                                    |

The stepper case is worth naming twice, because a wizard is the single worst structure for this path:
it is stateful, unaddressable, unmounts what you already answered, and changes under an agent that
re-reads. A review step that renders every answer is most of the fix.

## §4. Scripted crawls and runs

The far end of this path is a person writing a script rather than pasting once.

- is there a pagination contract that a script can walk — page tokens or offsets that are stable across
  requests, not a cursor tied to a scroll position?
- do rate limits and their headers exist, and does hitting one return `429` with `Retry-After` rather
  than a generic failure or a silent truncation?
- can a scripted run authenticate at all — a token, or only an interactive OAuth redirect?
- is `robots.txt` honest about what a polite crawler should skip, so a well-behaved script does not have
  to guess?
- do list endpoints return a total, so a script knows when it has everything?

A truncated result that looks complete is the failure mode here, and it is the one that produces
confidently wrong answers downstream.

## §5. Non-findings

- "add a copy button" with no named page and no named consumer
- export affordances on a surface nobody quotes
- demanding a `.md` twin of an interactive dashboard whose content is a live table — the export view is
  the right shape there, not a markdown mirror
- treating a missing copy button as equivalent to a missing accessible name; the first is friction, the
  second is a wall
