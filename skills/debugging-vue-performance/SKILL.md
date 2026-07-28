---
name: debugging-vue-performance
description: 'Debug Vue 3 performance issues using onRenderTracked, onRenderTriggered, app.config.performance, Vue DevTools profiler, and built-in optimization directives. Use when diagnosing slow Vue components, unnecessary reactivity triggers, or optimizing Vue render performance.'
interaction: autonomous
type: leaf
synergies:
  requires: [vue-best-practices]
  enhances: [systematic-debugging]
  domain: [vue, performance, debugging]
---

# Debugging Vue 3 Performance

Vue's fine-grained reactivity means most React-style "unnecessary rerender" bugs don't exist — components only update when their tracked reactive dependencies change. But Vue apps can still have performance issues from deep reactivity overhead, expensive computed properties, oversized component trees, and unoptimized lists.

## Quick Diagnostics Checklist

1. Enable `app.config.performance` → check Chrome DevTools Performance timeline
2. Add `onRenderTracked`/`onRenderTriggered` to suspect components → identify what triggers updates
3. Open Vue DevTools Timeline tab → record and inspect component render times
4. Check for deep reactive objects → consider `shallowRef`/`shallowReactive`
5. Look for large `v-for` lists → add `v-memo` or virtualize

## Step 1: Enable Performance Markers

In your app entry point (dev only):

```ts
// main.ts
const app = createApp(App)

if (import.meta.env.DEV) {
  app.config.performance = true
}
```

This adds Vue-specific timing markers to Chrome DevTools Performance panel:

- **Init**: time in `beforeCreate` → `created`
- **Render**: time to create the virtual DOM
- **Patch**: time to apply virtual DOM changes to the real DOM

Open Chrome DevTools → Performance → Record → interact with your app → stop. Look for `vue-` prefixed markers in the timeline.

## Step 2: onRenderTracked / onRenderTriggered

These composition API hooks tell you exactly **what reactive dependency** caused a component to re-render.

```vue
<script setup lang="ts">
import { ref, onRenderTracked, onRenderTriggered } from 'vue'

const items = ref([])
const filter = ref('')

// Called when a reactive dependency is TRACKED during render
// Fires on initial render for every tracked dependency
onRenderTracked((event) => {
  // event.target: the reactive object
  // event.key: which property was accessed
  // event.type: 'get' | 'has' | 'iterate'
  console.log('Tracked:', event.key, event.type)
})

// Called when a reactive dependency change TRIGGERS a re-render
// Fires on subsequent renders — tells you WHAT caused the update
onRenderTriggered((event) => {
  // Same shape as onRenderTracked, plus:
  // event.oldValue: previous value
  // event.newValue: new value
  // event.oldTarget: previous target state
  console.log('Triggered:', event.key, event.oldValue, '→', event.newValue)
  debugger // pause here to inspect the call stack
})
</script>
```

**Key difference:**

- `onRenderTracked` — fires during render to show which dependencies are being watched (initial + every render)
- `onRenderTriggered` — fires when a dependency mutation causes a re-render (tells you the "why")

### Using with Options API

```ts
export default {
  renderTracked(event) {
    console.log('Tracked:', event)
  },
  renderTriggered(event) {
    console.log('Triggered:', event)
  },
}
```

## Step 3: Vue DevTools Profiler

### Timeline Tab

1. Open Vue DevTools → Timeline tab
2. Click **Start recording**
3. Interact with your app
4. Stop recording
5. Inspect per-component render times

Look for:

- Components rendering when they shouldn't be
- Components taking >16ms (dropping below 60fps)
- Cascading renders (parent triggers unnecessary child updates)

### Component Inspector

Click any component in the tree to see:

- Current props, state, computed values
- Which reactive dependencies it tracks
- Render count

### Graph Tab

Shows dependency graph between components, files, and stylesheets — helps identify unnecessary coupling.

## Common Performance Patterns & Fixes

### 1. Props Stability — Avoid Triggering All List Items

```vue
<!-- ❌ BAD: Every ListItem re-renders when activeId changes -->
<ListItem v-for="item in list" :key="item.id" :id="item.id" :active-id="activeId" />

<!-- ✅ GOOD: Only items whose active status changed re-render -->
<ListItem v-for="item in list" :key="item.id" :id="item.id" :active="item.id === activeId" />
```

### 2. v-once — Skip Static Content

```vue
<!-- Rendered once, never updated again -->
<h1 v-once>{{ title }}</h1>

<!-- Entire subtree skipped on updates -->
<div v-once>
  <ComplexStaticChart :data="initialData" />
</div>
```

### 3. v-memo — Conditional Update Skipping (Vue 3.2+)

```vue
<!-- Only re-render list item when specific values change -->
<div v-for="item in list" :key="item.id" v-memo="[item.name, item.status]">
  <ExpensiveComponent :item="item" />
</div>

<!-- Skip re-render of entire section unless `filter` changes -->
<section v-memo="[filter]">
  <FilteredResults :filter="filter" :items="items" />
</section>
```

### 4. shallowRef / shallowReactive — Reduce Reactivity Overhead

For large datasets where you replace the whole object rather than mutating nested properties:

```ts
import { shallowRef } from 'vue'

// Deep reactivity on 10,000 objects = slow
const items = ref(largeDataset) // ❌ tracks every nested property

// Shallow — only tracks .value replacement
const items = shallowRef(largeDataset) // ✅ fast

// To update:
items.value = [...items.value, newItem] // ✅ triggers reactivity
items.value.push(newItem) // ❌ won't trigger
items.value[0].name = 'new' // ❌ won't trigger
```

### 5. Computed Stability (Vue 3.4+)

Computed properties only trigger effects when their value actually changes:

```ts
// ❌ BAD: Returns new object every time — always triggers downstream
const info = computed(() => ({
  isEven: count.value % 2 === 0,
}))

// ✅ GOOD: Return old value when content hasn't changed
const info = computed((oldValue) => {
  const newValue = { isEven: count.value % 2 === 0 }
  if (oldValue && oldValue.isEven === newValue.isEven) {
    return oldValue
  }
  return newValue
})
```

### 6. Async Components — Lazy Load Heavy Components

```ts
import { defineAsyncComponent } from 'vue'

const HeavyChart = defineAsyncComponent(() => import('./components/HeavyChart.vue'))
```

### 7. List Virtualization

For lists with 1000+ items, use a virtual scroller:

```bash
npm install vue-virtual-scroller
```

```vue
<template>
  <RecycleScroller :items="largeList" :item-size="50" key-field="id" v-slot="{ item }">
    <ListItem :item="item" />
  </RecycleScroller>
</template>
```

Libraries: `vue-virtual-scroller`, `vue-virtual-scroll-grid`, `vueuc/VVirtualList`

## Performance Anti-Patterns

| Anti-Pattern                                            | Why It's Slow                                     | Fix                                        |
| ------------------------------------------------------- | ------------------------------------------------- | ------------------------------------------ |
| Deep reactive on large arrays                           | Proxy traps on every property access              | `shallowRef` + immutable updates           |
| Inline object props in `v-for`                          | New object reference every render → child updates | Pass primitive props or stable refs        |
| Computed with side effects                              | Breaks caching, unpredictable re-evaluation       | Move side effects to `watch`/`watchEffect` |
| Too many component abstractions in lists                | Each component instance has overhead              | Flatten list item rendering for hot paths  |
| Mutating reactive arrays with `.push()` on `shallowRef` | Won't trigger reactivity                          | Spread into new array                      |

## Animation Performance (Vue + CSS)

Vue transitions and motion libraries can cause jank if they animate the wrong CSS properties. Source: `ibelick/ui-skills/fixing-motion-performance`.

### Safe vs. Unsafe Properties

Only `transform` and `opacity` are GPU-composited — everything else causes layout or paint:

```css
/* ✅ GPU-composited — no layout, no paint */
transform: translateX(100px);
opacity: 0.5;

/* ❌ Triggers layout (reflow) */
width, height, top, left, margin, padding

/* ❌ Triggers paint */
background-color, color, box-shadow, border-color
```

In Vue `<Transition>` components, keep enter/leave animations to `transform` and `opacity`:

```vue
<Transition name="slide">
  <div v-if="show">...</div>
</Transition>

<style>
.slide-enter-active,
.slide-leave-active {
  transition:
    transform 0.3s ease,
    opacity 0.3s ease; /* ✅ */
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}
</style>
```

### Layer Promotion with `will-change`

Use `will-change` on elements that animate frequently, but remove it once animation completes to avoid excessive GPU memory:

```ts
// In a Vue composable — add before animation, remove after
const el = ref<HTMLElement | null>(null)

function animateIn() {
  if (el.value) el.value.style.willChange = 'transform, opacity'
}

function onAnimationEnd() {
  if (el.value) el.value.style.willChange = 'auto' // release GPU layer
}
```

**Anti-patterns:**

- `will-change: all` — promotes everything, wastes GPU memory
- Static `will-change` on non-animating elements — costs memory without benefit
- Blur animations (`filter: blur()`) — extremely expensive; cap at 8px and never animate continuously

### Scroll-Linked Animation

Avoid scroll event listeners for animation — they run on the main thread and block input:

```ts
// ❌ Blocks main thread
window.addEventListener('scroll', () => {
  el.value.style.transform = `translateY(${scrollY * 0.5}px)`
})

// ✅ Use CSS Scroll Timeline (off-main-thread)
// Or use IntersectionObserver for trigger-based animations
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((e) => e.target.classList.toggle('visible', e.isIntersecting))
  },
  { threshold: 0.1 }
)
observer.observe(el.value)
```

## Core Web Vitals Baselines

Use these thresholds when diagnosing Vue app performance against Lighthouse / CrUX data. Sources: `addyosmani/web-quality-skills`, `cloudflare/skills`.

| Metric                         | Good    | Needs Improvement | Poor    |
| ------------------------------ | ------- | ----------------- | ------- |
| LCP (Largest Contentful Paint) | < 2.5s  | < 4s              | > 4s    |
| FCP (First Contentful Paint)   | < 1.8s  | < 3s              | > 3s    |
| TBT (Total Blocking Time)      | < 200ms | < 600ms           | > 600ms |
| CLS (Cumulative Layout Shift)  | < 0.1   | < 0.25            | > 0.25  |
| TTFB (Time to First Byte)      | < 800ms | < 1.8s            | > 1.8s  |

### Resource Budgets for Vue SPAs

Keep these limits to stay within good Lighthouse scores:

| Resource                | Budget   |
| ----------------------- | -------- |
| Total page              | < 1.5 MB |
| JavaScript (compressed) | < 300 KB |
| CSS (compressed)        | < 100 KB |
| Above-fold images       | < 500 KB |
| Fonts                   | < 100 KB |
| Third-party scripts     | < 200 KB |

### Diagnosing CLS in Vue Apps

CLS spikes often come from async content loading — images without dimensions, late-loading fonts, or dynamic content insertion. In Vue:

```vue
<!-- ❌ Image without dimensions — causes layout shift when it loads -->
<img :src="imageUrl" alt="..." />
```

For font loading, use `font-display: swap` and preload critical fonts in `index.html`:

```html
<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin />
```

### Diagnosing Render-Blocking in Vue + Vite Apps

Vue apps built with Vite rarely have render-blocking scripts (modules are deferred by default), but watch for:

- Large synchronous chunks in the critical path — use dynamic `import()` to split
- Blocking CSS from third-party stylesheets — add `media="print"` + `onload` swap trick
- LCP image not preloaded — if your hero image is in a Vue component, Vite won't auto-preload it; add `<link rel="preload">` manually in `index.html`

## External Vue Skills Ecosystem

Community-maintained agent skills for Vue development:

- **[vuejs-ai/skills](https://github.com/vuejs-ai/skills)** (2k★) — 8 skills including `vue-debug-guides` for runtime debugging
- **[antfu/skills](https://github.com/antfu/skills)** — Anthony Fu's collection for Vue/Vite/Nuxt, generated from official docs
- **[vueuse/vueuse-skills](https://github.com/vueuse/vueuse-skills)** — Skills for VueUse composables
- **[onmax/nuxt-skills](https://github.com/onmax/nuxt-skills)** — Nuxt-specific skills

Install via: `npx skills add vuejs-ai/skills`
