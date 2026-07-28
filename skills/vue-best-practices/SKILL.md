---
name: vue-best-practices
description: 'Vue 3 best practices with Composition API, script setup, and TypeScript. Covers reactivity, SFC structure, component design, data flow, composables, and performance optimization. Use when working on Vue components or .vue files.'
interaction: autonomous
type: leaf
license: MIT
metadata:
  author: github.com/vuejs-ai
  version: '18.0.0'
synergies:
  requires: []
  enhances: [debugging-vue-performance, vue-pinia-best-practices, vue-debug-guides]
  conflicts: []
  domain: [vue, frontend]
---

# Vue Best Practices Workflow

Use this skill as an instruction set. Follow the workflow in order unless the user explicitly asks for a different order.

## Core Principles

- **Keep state predictable:** one source of truth, derive everything else.
- **Make data flow explicit:** Props down, Events up for most cases.
- **Favor small, focused components:** easier to test, reuse, and maintain.
- **Avoid unnecessary re-renders:** use computed properties and watchers wisely.
- **Readability counts:** write clear, self-documenting code.

## 1) Confirm architecture before coding (required)

- Default stack: Vue 3 + Composition API + `<script setup lang="ts">`.
- If the project explicitly uses Options API, load `vue-options-api-best-practices` skill if available.
- If the project explicitly uses JSX, load `vue-jsx-best-practices` skill if available.

### 1.1 Must-read core references (required)

- Before implementing any Vue task, make sure to read and apply these core references:
  - `references/reactivity.md`
  - `references/sfc.md`
  - `references/component-data-flow.md`
  - `references/composables.md`
- Keep these references in active working context for the entire task, not only when a specific issue appears.

### 1.2 Plan component boundaries before coding (required)

Create a brief component map before implementation for any non-trivial feature.

- Define each component's single responsibility in one sentence.
- Keep entry/root and route-level view components as composition surfaces by default.
- Move feature UI and feature logic out of entry/root/view components unless the task is intentionally a tiny single-file demo.
- Define props/emits contracts for each child component in the map.
- Prefer a feature folder layout (`components/<feature>/...`, `composables/use<Feature>.ts`) when adding more than one component.

## 2) Apply essential Vue foundations (required)

These are essential, must-know foundations. Apply all of them in every Vue task using the core references already loaded in section `1.1`.

### Reactivity

- Must-read reference from `1.1`: [reactivity](references/reactivity.md)
- Keep source state minimal (`ref`/`reactive`), derive everything possible with `computed`.
- Use watchers for side effects if needed.
- Avoid recomputing expensive logic in templates.
- Prefer `shallowRef` over `ref` when deep reactivity is not needed — avoids recursive observation overhead on large objects.
- Use `defineModel()` macro for two-way binding in child components instead of manually pairing a `modelValue` prop with an `update:modelValue` emit.

### SFC structure and template safety

- Must-read reference from `1.1`: [sfc](references/sfc.md)
- Keep SFC sections in this order: `<script>` → `<template>` → `<style>`.
- Keep SFC responsibilities focused; split large components.
- Keep templates declarative; move branching/derivation to script.
- Apply Vue template safety rules (`v-html`, list rendering, conditional rendering choices).

### Keep components focused

Split a component when it has **more than one clear responsibility** (e.g. data orchestration + UI, or multiple independent UI sections).

- Prefer **smaller components + composables** over one “mega component”
- Move **UI sections** into child components (props in, events out).
- Move **state/side effects** into composables (`useXxx()`).

Apply objective split triggers. Split the component if **any** condition is true:

- It owns both orchestration/state and substantial presentational markup for multiple sections.
- It has 3+ distinct UI sections (for example: form, filters, list, footer/status).
- A template block is repeated or could become reusable (item rows, cards, list entries).

Entry/root and route view rule:

- Keep entry/root and route view components thin: app shell/layout, provider wiring, and feature composition.
- Do not place full feature implementations in entry/root/view components when those features contain independent parts.
- For CRUD/list features (todo, table, catalog, inbox), split at least into:
  - feature container component
  - input/form component
  - list (and/or item) component
  - footer/actions or filter/status component
- Allow a single-file implementation only for very small throwaway demos; if chosen, explicitly justify why splitting is unnecessary.

### Component data flow

- Must-read reference from `1.1`: [component-data-flow](references/component-data-flow.md)
- Use props down, events up as the primary model.
- Use `v-model` only for true two-way component contracts.
- Use provide/inject only for deep-tree dependencies or shared context.
- Keep contracts explicit and typed with `defineProps`, `defineEmits`, and `InjectionKey` as needed.

### Composables

- Must-read reference from `1.1`: [composables](references/composables.md)
- Extract logic into composables when it is reused, stateful, or side-effect heavy.
- Keep composable APIs small, typed, and predictable.
- Separate feature logic from presentational components.
- **Check VueUse first** — before building a custom composable, check if `@vueuse/core` already provides it (e.g. `useLocalStorage`, `useDebounceFn`, `useIntersectionObserver`). Prefer the battle-tested composable over bespoke code.
- Use `effectScope()` to group reactive effects inside a composable and dispose them together with a single `scope.stop()` call — avoids leaking watchers when the composable is used conditionally or outside a component.

### Template and styling conventions

These rules apply to all Vue template and styling work:

- Use `h-dvh` instead of `h-screen` — handles mobile browser chrome correctly.
- Use `text-balance` on headings and `text-pretty` on body/paragraphs for better line wrapping.
- Use `tabular-nums` (or `font-variant-numeric: tabular-nums`) for data columns and numbers that need alignment.
- Use `size-*` for square elements instead of separate `w-*` + `h-*`.
- Use a fixed z-index scale — no arbitrary `z-[9999]` values. Semantic scale: dropdown(100) → sticky(200) → modal-backdrop(300) → modal(400) → toast(500) → tooltip(600).
- Use `<Teleport to="body">` for overlays, dropdowns, and modals. Never render positioned overlays inside `overflow: hidden` containers — they will be clipped.
- Never block paste in `<input>` or `<textarea>` elements.
- If the project has a `cn()` utility (`clsx` + `tailwind-merge`), use it for merging external `class` prop overrides with component defaults. For internal-only conditional classes (no prop override), prefer `twJoin` — it skips conflict resolution and is faster.

## 2b) Vite build-tool conventions

Apply these when working in a Vite-based Vue project:

- Always use ESM; avoid `require()` / CommonJS in source files.
- Read environment variables through `import.meta.env` — never through `process.env` in client code.
- Use `import.meta.glob` for lazy-loading sets of modules (e.g. auto-importing route components or locale files).
- Keep Vite config in `vite.config.ts` using `defineConfig`; use `loadEnv` for environment-specific overrides instead of dotenv packages.

## 3) Consider optional features only when requirements call for them

### 3.1 Standard optional features

Do not add these by default. Load the matching reference only when the requirement exists.

- Slots: parent needs to control child content/layout -> [component-slots](references/component-slots.md)
- Fallthrough attributes: wrapper/base components must forward attrs/events safely -> [component-fallthrough-attrs](references/component-fallthrough-attrs.md)
- Built-in component `<KeepAlive>` for stateful view caching -> [component-keep-alive](references/component-keep-alive.md)
- Built-in component `<Teleport>` for overlays/portals -> [component-teleport](references/component-teleport.md)
- Built-in component `<Suspense>` for async subtree fallback boundaries -> [component-suspense](references/component-suspense.md)
- Animation-related features: pick the simplest approach that matches the required motion behavior.
  - Built-in component `<Transition>` for enter/leave effects -> [transition](references/component-transition.md)
  - Built-in component `<TransitionGroup>` for animated list mutations -> [transition-group](references/component-transition-group.md)
  - Class-based animation for non-enter/leave effects -> [animation-class-based-technique](references/animation-class-based-technique.md)
  - State-driven animation for user-input-driven animation -> [animation-state-driven-technique](references/animation-state-driven-technique.md)

### 3.2 Less-common optional features

Use these only when there is explicit product or technical need.

- Directives: behavior is DOM-specific and not a good composable/component fit -> [directives](references/directives.md)
- Async components: heavy/rarely-used UI should be lazy loaded -> [component-async](references/component-async.md)
- Render functions only when templates cannot express the requirement -> [render-functions](references/render-functions.md)
- Plugins when behavior must be installed app-wide -> [plugins](references/plugins.md)
- State management patterns: app-wide shared state crosses feature boundaries -> [state-management](references/state-management.md)

## 4) Run performance optimization after behavior is correct

Performance work is a post-functionality pass. Do not optimize before core behavior is implemented and verified.

- Large list rendering bottlenecks -> [perf-virtualize-large-lists](references/perf-virtualize-large-lists.md)
- Static subtrees re-rendering unnecessarily -> [perf-v-once-v-memo-directives](references/perf-v-once-v-memo-directives.md)
- Over-abstraction in hot list paths -> [perf-avoid-component-abstraction-in-lists](references/perf-avoid-component-abstraction-in-lists.md)
- Expensive updates triggered too often -> [updated-hook-performance](references/updated-hook-performance.md)
- Off-screen content causing unnecessary layout/paint work -> use CSS `content-visibility: auto` with `contain-intrinsic-size: auto <fallback>` on repeating sections, tab panels, below-fold content, and long scrollable lists. The browser skips rendering until the element approaches the viewport. Accessibility-safe (content stays in DOM + a11y tree, find-in-page works). Baseline 2024 — all modern browsers.

## 5) Final self-check before finishing

- Core behavior works and matches requirements.
- All must-read references were read and applied.
- Reactivity model is minimal and predictable.
- SFC structure and template rules are followed.
- Components are focused and well-factored, splitting when needed.
- Entry/root and route view components remain composition surfaces unless there is an explicit small-demo exception.
- Component split decisions are explicit and defensible (responsibility boundaries are clear).
- Data flow contracts are explicit and typed.
- Composables are used where reuse/complexity justifies them.
- Moved state/side effects into composables if applicable
- VueUse checked before writing custom composables where applicable.
- `shallowRef` used instead of `ref` where deep reactivity is not needed.
- `defineModel()` used for two-way binding child components.
- Optional features are used only when requirements demand them.
- Performance changes were applied only after functionality was complete.
- Vite: `import.meta.env` used (not `process.env`), ESM-only source files.
