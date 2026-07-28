---
name: comfyui-frontend
description: 'Convention knowledge for ComfyUI_frontend. Vue 3 + TypeScript + Tailwind 4 + Pinia. Covers patterns agents commonly get wrong.'
type: leaf
---

# ComfyUI Frontend Conventions

Repo: `Comfy-Org/ComfyUI_frontend` — Vue 3.5+ / TypeScript / Vite / Tailwind 4 / Pinia

## Stack Quick-Ref

| Layer         | Choice                                                                  |
| ------------- | ----------------------------------------------------------------------- |
| Framework     | Vue 3.5+ Composition API (`<script setup lang="ts">`)                   |
| Styling       | Tailwind 4 — semantic tokens, NO `dark:` variant, NO `!important`       |
| State         | Pinia stores in `src/stores/` — named `*Store.ts`                       |
| Composables   | `src/composables/` — named `useXyz.ts`                                  |
| Components    | PascalCase `.vue` files — NO new PrimeVue usage                         |
| UI primitives | shadcn/vue + Reka UI                                                    |
| Utilities     | `es-toolkit` (not lodash)                                               |
| i18n          | `vue-i18n` composition API — keys in `src/locales/en/main.json`         |
| Tests         | Vitest (unit `*.test.ts` colocated) / Playwright (E2E `browser_tests/`) |
| Lint/Format   | oxlint + ESLint + oxfmt — run `pnpm lint` and `pnpm format`             |
| Package mgr   | pnpm only — `pnpx`/`pnpm dlx`, never `npx`                              |
| Build         | Nx-orchestrated Vite                                                    |

## Critical Anti-Patterns (agents get these wrong)

1. **Never use `any` or `as any`** — fix the underlying type
2. **Never use `:class="[]"`** — always `cn()` from `@/utils/tailwindUtil`
3. **Never use `dark:` Tailwind variant** — use semantic tokens like `bg-node-component-surface`
4. **Never use barrel files** (`index.ts` re-exports) within `src/`
5. **Separate type imports**: `import type { Foo }` on its own line, NOT `import { bar, type Foo }`
6. **No `withDefaults`** — use Vue 3.5 destructured props: `const { x = 'default' } = defineProps<{...}>()`
7. **Prefer `defineModel`** over manual prop + emit for v-model bindings
8. **No `--no-verify`** when committing — ever

## Store Pattern

```typescript
// src/stores/exampleStore.ts
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useExampleStore = defineStore('example', () => {
  const items = ref<Item[]>([])
  const count = computed(() => items.value.length)
  function addItem(item: Item) {
    items.value.push(item)
  }
  return { items, count, addItem }
})
```

- Tests colocated: `exampleStore.test.ts` next to `exampleStore.ts`
- Keep internal state private — only export what's used externally

## Import Paths

- Always use `@/` alias (maps to `src/`): `import { api } from '@/scripts/api'`
- Platform-specific code lives under `src/platform/`
- Services under `src/services/`, schemas under `src/schemas/`

## Commit Messages

Use `prefix:` format: `feat:`, `fix:`, `test:`, `refactor:`. Never mention AI/Claude.

## Skill Combos

When working in this repo, load companion skills based on what you're touching:

| File pattern                    | Also load skill             | Why                                                                                             |
| ------------------------------- | --------------------------- | ----------------------------------------------------------------------------------------------- |
| `src/stores/*.ts`               | `vue-pinia-best-practices`  | Store reactivity gotchas, setup pattern, destructuring                                          |
| `src/composables/use*.ts`       | —                           | Use MaybeRef/MaybeRefOrGetter input patterns for flexible composable APIs                       |
| `*.vue` files                   | `vue-best-practices`        | Composition API, SFC structure, component design                                                |
| `*.vue` with JSX/TSX            | —                           | Remember Vue JSX differs from React JSX (class vs className)                                    |
| `src/router/` or route config   | —                           | Follow standard navigation guard, route param, and lifecycle patterns                           |
| `*.test.ts` or `browser_tests/` | —                           | Use Vitest for unit tests, Vue Test Utils, and Playwright for E2E                               |
| Performance investigation       | `debugging-vue-performance` | onRenderTracked, profiler, optimization directives                                              |
| Canvas widget overlays          | `html-in-canvas`            | New HTML-in-Canvas API for rendering HTML as canvas children (experimental, Chrome Canary only) |

## Design Standards

Before implementing any user-facing feature, consult the **Comfy Design Standards** Figma file via MCP.

See `design-standards.md` in this skill's directory for Figma file keys, section node IDs, and fetch patterns. Always pull live from Figma — do not rely on cached rules.

## Quality Gates (must pass before PR)

```bash
pnpm typecheck && pnpm lint && pnpm format:check && pnpm knip && pnpm test:unit
```

## Companion Skills (auto-load when relevant)

| Skill                       | When to load                                             |
| --------------------------- | -------------------------------------------------------- |
| `vue-best-practices`        | Writing/editing `.vue` files                             |
| `vue-pinia-best-practices`  | Working on `src/stores/*.ts`                             |
| `debugging-vue-performance` | Diagnosing slow renders or reactivity issues             |
| `agent-browser`             | Visual QA — verify rendered output on running dev server |
