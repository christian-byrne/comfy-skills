# Comfy Design Standards — Live Reference

When implementing or reviewing **any user-facing feature** in ComfyUI_frontend, you MUST consult the Comfy Design Standards Figma file before writing UI code.

## How to Fetch

Use the Figma MCP tool `get_figma_data` to pull the current design standards:

```
File key: <the Comfy Design Standards file key — ask the design team>
Root node: 0-1
```

The file key is deliberately not written down here: this skill is published
publicly and the design file is internal. Anyone on the team can supply it, and
the node map below is meaningless without it.

### Section Node Map

| Section              | Node ID   | When to consult                                                               |
| -------------------- | --------- | ----------------------------------------------------------------------------- |
| Hover States         | `1-2`     | Adding/modifying interactive elements (buttons, inputs, links, nav items)     |
| Click Targets        | `4-243`   | Adding clickable elements, especially small ones (icons, handles, connectors) |
| Affordances          | `15-2202` | Any interactive element — ensuring visual feedback on interaction             |
| Feedback             | `15-2334` | User actions that need confirmation, success/error states                     |
| Slips and How to Fix | `15-2337` | Error prevention, undo patterns, destructive actions                          |
| Design Pillars       | `15-2340` | New features, architectural UI decisions                                      |
| The User             | `16-2348` | User flows, onboarding, accessibility                                         |
| References           | `16-2342` | External design references and inspiration                                    |

### Fetch Pattern

```typescript
// Fetch the specific section relevant to your task
get_figma_data({ fileKey: '<design-standards-file-key>', nodeId: '<node-id>', depth: 3 })
```

For broad UI work, fetch the root node at depth 1 first to see all sections, then drill into relevant ones.

The Figma file is the single source of truth. Apply only what is defined there — do not invent additional rules.

## Component Library Reference

The Figma file contains component definitions. When implementing these components, fetch the component details:

```
// Button component set
Component set ID: 4:314 (Button/Default)
// Search component set
Component set ID: 4:2366 (Search)
// Node component set
Component set ID: 4:4739 (Base Node Example)
```

## Integration with Design System Code

The frontend uses shadcn/vue + Reka UI primitives with Tailwind 4 semantic tokens. When the Figma standards specify a color or spacing value, map it to the appropriate semantic token — never hardcode hex values.
