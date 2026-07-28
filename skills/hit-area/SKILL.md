---
name: hit-area
description: 'Install and use hit-area Tailwind CSS v4 utility classes to expand interactive element hit areas without layout impact. Distributed via shadcn registry. Use when working on Tailwind v4 projects and need to fix dead zones, expand touch targets, or improve click area UX.'
type: leaf
---

# hit-area — Tailwind CSS Hit Area Utilities

Expand the clickable area of interactive elements without affecting layout. Uses CSS pseudo-elements under the hood.

**Source:** [bazza.dev/craft/2026/hit-area](https://bazza.dev/craft/2026/hit-area) by Kian Bazza

**Requires:** Tailwind CSS v4 + shadcn (`components.json` configured)

## Installation

```bash
npx shadcn@latest add https://bazza.dev/r/hit-area
```

Adds utility definitions to your `globals.css` (or whichever file is configured as `tailwind.css` in `components.json`).

## Utilities Reference

### Uniform (all sides)

```html
<button class="hit-area-6">...</button>
```

### Individual sides

```html
<button class="hit-area-l-4">...</button>
<!-- left -->
<button class="hit-area-r-4">...</button>
<!-- right -->
<button class="hit-area-t-4">...</button>
<!-- top -->
<button class="hit-area-b-4">...</button>
<!-- bottom -->
```

### Axis shorthands

```html
<button class="hit-area-x-4">...</button>
<!-- horizontal -->
<button class="hit-area-y-6">...</button>
<!-- vertical -->
```

### Arbitrary values

```html
<button class="hit-area-[21px]">...</button>
<button class="hit-area-l-[3rem]">...</button>
<button class="hit-area-b-[calc(100%+1rem)]">...</button>
```

### Composing

Classes stack and merge:

```html
<button class="hit-area-x-8 hit-area-b-2">...</button>
<button class="hit-area-l-16 hit-area-r-4 hit-area-b-6 hit-area-t-2">...</button>
```

### Debugging

Visualize hit areas with a dashed border overlay:

```html
<button class="hit-area-6 hit-area-debug">...</button>
```

Remove `hit-area-debug` before shipping.

## Common Patterns

| Scenario                          | Recommended                                         |
| --------------------------------- | --------------------------------------------------- |
| Table checkbox in padded cell     | `hit-area-x-4 hit-area-y-2` or expand to fill cell  |
| Sidebar nav items with `gap-y-px` | `hit-area-y-1` to cover gaps                        |
| Icon-only toolbar buttons         | `hit-area-4` for minimum 44×44px total              |
| Close × button in corner          | `hit-area-b-4 hit-area-l-4` toward container center |

## Shadcn Registry Pattern

`hit-area` is a live example of the shadcn registry distribution pattern — source code delivered via HTTP, not npm. The install URL (`https://bazza.dev/r/hit-area`) serves a `registry-item.json` that the CLI resolves into CSS injected into your project. To host your own registry items using the same pattern, see the [shadcn registry docs](https://ui.shadcn.com/docs/registry).

## How It Works

Each utility sets `position: relative` on the element and creates a `::before` pseudo-element with:

- `position: absolute` with negative inset values (via CSS custom properties `--hit-area-t/r/b/l`)
- `pointer-events: inherit` so clicks pass through to the parent
- No layout impact — the pseudo-element is taken out of flow
