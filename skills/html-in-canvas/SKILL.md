---
name: html-in-canvas
description: 'Set up and use the HTML-in-Canvas API to render HTML elements as canvas children. Covers feature detection, layoutsubtree, drawElementImage, paint events, WebGL textures, and migration from sibling overlays. Use when asked to set up html-in-canvas, use canvas HTML elements, render HTML in canvas, or migrate canvas overlays.'
interaction: autonomous
type: leaf
---

# HTML-in-Canvas

Guide for using the [WICG HTML-in-Canvas API](https://github.com/WICG/html-in-canvas) to render fully laid-out, styled HTML elements into `<canvas>` (2D, WebGL, WebGPU).

## Browser Support (as of April 2026)

| Browser       | Status                                            |
| ------------- | ------------------------------------------------- |
| Chrome Canary | Behind flag `chrome://flags/#canvas-draw-element` |
| Chrome Stable | Not yet                                           |
| Firefox       | No implementation                                 |
| Safari        | No implementation                                 |
| Edge          | No implementation                                 |

**This API is pre-standardization.** Use only for experimentation, prototypes, or behind feature flags.

## Feature Detection

```typescript
function supportsHtmlInCanvas(): boolean {
  const canvas = document.createElement('canvas')
  return 'layoutSubtree' in canvas
}
```

Always gate usage behind feature detection:

```typescript
if (supportsHtmlInCanvas()) {
  canvas.layoutSubtree = true
} else {
  // Fall back to sibling overlay pattern
}
```

## Core Setup

### Step 1: Enable `layoutsubtree`

```html
<canvas id="canvas" layoutsubtree>
  <!-- HTML children go here — they're laid out but invisible until drawn -->
  <div id="widget">
    <label for="value">Value:</label>
    <input id="value" type="range" min="0" max="100" />
  </div>
</canvas>
```

The `layoutsubtree` attribute:

- Opts children into browser layout and hit testing
- Children are **invisible** until explicitly drawn via `drawElementImage()`
- Children remain in the accessibility tree and respond to focus
- Direct children get a stacking context and paint containment

### Step 2: Draw with `drawElementImage()`

```typescript
const canvas = document.getElementById('canvas') as HTMLCanvasElement
const ctx = canvas.getContext('2d')!
const widget = document.getElementById('widget')!

canvas.onpaint = () => {
  ctx.reset()

  // Draw your canvas background, shapes, etc.
  ctx.fillStyle = '#1a1a2e'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  // Draw the HTML element at position (100, 50)
  const transform = ctx.drawElementImage(widget, 100, 50)

  // CRITICAL: Sync DOM position for hit testing + accessibility
  widget.style.transform = transform.toString()
}
```

**Key points:**

- Returns a `DOMMatrix` — you MUST apply it to `element.style.transform` for clicks, focus, and a11y to work
- Respects the canvas CTM (rotations, scales, translations all apply)
- CSS transforms on the element itself are ignored for drawing (but still affect hit testing)
- Overflowing content is clipped to the element's border box

### Step 3: Handle Canvas Sizing

```typescript
// Size canvas grid to device pixel ratio to prevent blurriness
const observer = new ResizeObserver(([entry]) => {
  canvas.width = entry.devicePixelContentBoxSize[0].inlineSize
  canvas.height = entry.devicePixelContentBoxSize[0].blockSize
})
observer.observe(canvas, { box: 'device-pixel-content-box' })
```

### Step 4: Use `requestPaint()` for Animation

```typescript
// paint event only fires when children change.
// Use requestPaint() for continuous animation (like rAF):
function animate() {
  canvas.requestPaint()
  requestAnimationFrame(animate)
}
animate()
```

## `drawElementImage()` Overloads

Mirrors `drawImage()` — same signature patterns:

```typescript
// Draw at position
ctx.drawElementImage(element, dx, dy)

// Draw at position with destination size
ctx.drawElementImage(element, dx, dy, dwidth, dheight)

// Draw sub-rectangle of element
ctx.drawElementImage(element, sx, sy, swidth, sheight, dx, dy)

// Draw sub-rectangle with destination size
ctx.drawElementImage(element, sx, sy, swidth, sheight, dx, dy, dwidth, dheight)
```

## Common Patterns

### Form Controls in Canvas

```html
<canvas id="editor" layoutsubtree>
  <form id="properties-panel">
    <label>Name: <input type="text" id="name" /></label>
    <label>Color: <input type="color" id="color" /></label>
    <button type="submit">Apply</button>
  </form>
</canvas>
```

```typescript
canvas.onpaint = () => {
  ctx.reset()
  drawBackground(ctx)
  drawNodes(ctx)

  // Draw the form — it's fully interactive (typing, clicking, focus all work)
  const t = ctx.drawElementImage(propertiesPanel, panelX, panelY)
  propertiesPanel.style.transform = t.toString()
}
```

### Text Overlays with Canvas Effects

```typescript
canvas.onpaint = () => {
  ctx.reset()

  // Canvas graphics
  ctx.filter = 'blur(3px)'
  ctx.drawImage(backgroundImage, 0, 0)
  ctx.filter = 'none'

  // HTML text — fully styled, accessible, selectable
  const t = ctx.drawElementImage(titleElement, 20, 20)
  titleElement.style.transform = t.toString()
}
```

### Multiple Elements with Transforms

```typescript
canvas.onpaint = () => {
  ctx.reset()

  // Each element can have independent canvas transforms
  ctx.save()
  ctx.rotate((15 * Math.PI) / 180)
  const t1 = ctx.drawElementImage(element1, 50, 50)
  element1.style.transform = t1.toString()
  ctx.restore()

  ctx.save()
  ctx.scale(1.5, 1.5)
  const t2 = ctx.drawElementImage(element2, 200, 100)
  element2.style.transform = t2.toString()
  ctx.restore()
}
```

## WebGL: HTML as Texture

```typescript
const gl = canvas.getContext('webgl')!

// Use an HTML element as a texture source
gl.texElementImage2D(
  gl.TEXTURE_2D,
  0, // level
  gl.RGBA, // internal format
  gl.RGBA, // format
  gl.UNSIGNED_BYTE, // type
  element
)
```

## WebGPU: HTML as Texture

```typescript
const device = await navigator.gpu.requestAdapter().then((a) => a!.requestDevice())
const queue = device.queue

queue.copyElementImageToTexture(
  { element }, // source
  { texture } // destination GPUImageCopyTextureTagged
)
```

## OffscreenCanvas (Worker Thread)

For offloading rendering to a worker:

**Main thread:**

```typescript
const worker = new Worker('canvas-worker.js')
const offscreen = canvas.transferControlToOffscreen()
worker.postMessage({ canvas: offscreen }, [offscreen])

canvas.onpaint = () => {
  const elementImage = canvas.captureElementImage(widget)
  worker.postMessage({ elementImage }, [elementImage])
}

// Receive transform back from worker for DOM sync
worker.onmessage = (e) => {
  if (e.data.transform) {
    widget.style.transform = new DOMMatrix(e.data.transform).toString()
  }
}
```

**Worker (`canvas-worker.js`):**

```typescript
let ctx: OffscreenCanvasRenderingContext2D

self.onmessage = (e) => {
  if (e.data.canvas) {
    ctx = e.data.canvas.getContext('2d')!
  }
  if (e.data.elementImage) {
    ctx.reset()
    const transform = ctx.drawElementImage(e.data.elementImage, 100, 0)
    self.postMessage({ transform: transform.toFloat64Array() })
  }
}
```

## Migration: Sibling Overlays → Canvas Children

### Before (sibling overlay pattern)

```html
<div class="canvas-container" style="position: relative;">
  <canvas id="canvas"></canvas>
  <!-- Overlay positioned absolutely on top of canvas -->
  <div id="widget" style="position: absolute; top: 50px; left: 100px;">
    <input type="text" />
  </div>
</div>
```

### After (HTML-in-Canvas)

```html
<canvas id="canvas" layoutsubtree>
  <!-- Now a true child of the canvas -->
  <div id="widget">
    <input type="text" />
  </div>
</canvas>

<script>
  canvas.onpaint = () => {
    ctx.reset()
    drawCanvasContent(ctx)
    const t = ctx.drawElementImage(widget, 100, 50)
    widget.style.transform = t.toString()
  }
</script>
```

### Migration checklist

1. Add `layoutsubtree` to the `<canvas>` element
2. Move overlay elements from siblings to children of `<canvas>`
3. Remove `position: absolute` and manual coordinate CSS from moved elements
4. Add `drawElementImage()` calls in the `paint` event handler
5. Apply the returned `DOMMatrix` to each element's `style.transform`
6. Remove manual hit-testing / coordinate mapping code (the browser handles it now)
7. Replace `requestAnimationFrame` render loops with `onpaint` + `requestPaint()`
8. Test: keyboard focus, screen readers, click targets all still work

## Security Constraints

`drawElementImage()` exposes element pixels to script (via `getImageData`). The following are **blocked from rendering:**

- Cross-origin iframes, images, SVG `<use>`, CSS `url()` from different origins
- System colors and OS theme details
- Visited link styles (`:visited`)
- Spellcheck/grammar markers
- Pending autofill values

If you need cross-origin images inside drawn elements, set appropriate CORS headers.

## Gotchas

1. **Always sync transforms** — forgetting `element.style.transform = transform.toString()` breaks all interactivity
2. **Children must be direct children** — nested wrapper elements won't work with `drawElementImage()`; the element must be a direct child of the `<canvas>`
3. **`display: none` breaks it** — elements must have generated boxes to be drawn
4. **DOM mutations in `paint` apply next frame** — canvas drawing commands apply immediately, but DOM changes wait until the next frame
5. **CSS transforms on elements are ignored for drawing** — only the canvas CTM applies; use canvas transforms instead
6. **No `paint` event for transform-only changes** — changing only `element.style.transform` doesn't trigger `paint`; call `requestPaint()` if you need a redraw

## Accessibility

HTML-in-Canvas is one of the most significant a11y improvements for canvas-based UIs. Previously, canvas fallback content was manually maintained and easily drifted from what was actually rendered.

### Why It Matters

With `layoutsubtree`, child elements:

- **Stay in the accessibility tree** — screen readers see real DOM elements, not fake ARIA overlays
- **Respond to focus** — Tab, Shift+Tab, and focus rings work natively
- **Support keyboard interaction** — form controls (inputs, buttons, selects) work without custom key handlers
- **Match visual output** — the drawn position IS the DOM position (via transform sync)

### Critical: Transform Sync for A11y

If you skip `element.style.transform = transform.toString()`, the DOM element stays at its layout position (top-left of the canvas), while visually it appears elsewhere. This means:

- Screen readers announce elements in the wrong spatial order
- Click/tap targets don't match visual positions
- Focus outlines appear in the wrong place

**Always apply the returned DOMMatrix.** This is not optional for accessible UIs.

### Patterns

```html
<canvas id="editor" layoutsubtree>
  <!-- Use semantic HTML — it's real DOM now -->
  <nav id="toolbar" aria-label="Editor toolbar">
    <button id="undo" aria-label="Undo">↩</button>
    <button id="redo" aria-label="Redo">↪</button>
  </nav>
  <div id="node-label" role="heading" aria-level="3">My Node</div>
</canvas>
```

### Verifying A11y

1. **Tab through** — focus should follow visual order, not DOM order
2. **Screen reader** — elements should be announced with correct spatial context
3. **Inspect a11y tree** — Chrome DevTools → Accessibility tab should show the canvas children as normal DOM nodes
4. **High contrast mode** — drawn elements inherit system colors (allowed by the security model)

## References

- [WICG Explainer](https://github.com/WICG/html-in-canvas)
<!-- docs-linter-disable-next-link -->
- [Chrome Flag](chrome://flags/#canvas-draw-element) (Chrome Canary only)
- [Security & Privacy Questionnaire](https://github.com/WICG/html-in-canvas/blob/main/security-privacy-questionnaire.md)
