# Visual Performance Optimization

Optimize rendering performance for WebGPU/WASM/canvas applications. The agent edits code, Vite hot-reloads, Playwright collects frametimes, and the loop keeps or reverts based on p99.9 frametime.

This domain is unique: the agent can **see its own work** via screenshots, enabling visual quality checks alongside performance metrics.

## Architecture

```
Agent edits code → Vite HMR hot-reloads → Playwright collects frametimes
                                        → Playwright takes screenshot (agent views)
                                        → Extract p99.9 → keep or revert
```

**Prerequisites:**

- Vite dev server running with HMR (use tmux)
- Playwright with Chromium installed (`pnpm exec playwright install chromium`)
- WebGPU requires `--enable-unsafe-webgpu` and `--enable-features=Vulkan` flags in Chromium launch args
- The app must expose frametime data (see Metric Extraction below)

## Typical Metrics

| Metric Name         | Unit         | Direction | When to Use                                   |
| ------------------- | ------------ | --------- | --------------------------------------------- |
| `p999_frametime_ms` | milliseconds | ↓ lower   | Primary — captures worst-case jank/glitches   |
| `p99_frametime_ms`  | milliseconds | ↓ lower   | Secondary — smoother distribution             |
| `p50_frametime_ms`  | milliseconds | ↓ lower   | Median frame budget (should be <16.67ms@60Hz) |
| `dropped_frames`    | count        | ↓ lower   | Frames exceeding 2× target frame budget       |
| `gpu_memory_mb`     | megabytes    | ↓ lower   | WebGPU buffer/texture memory                  |

**Always optimize p99.9 as the primary metric.** Median frametime is misleading — a smooth 60fps with periodic 100ms spikes feels terrible. The tail latency is where glitches live.

## Metric Extraction

### Option 1: PerformanceObserver (Recommended)

Add this to the app's entry point. It posts frametime stats to a known endpoint or writes to `window.__FRAMETIMES__`:

```typescript
// Add to app entry — DO NOT modify during autoresearch
const frametimes: number[] = []
let lastTimestamp = 0

function measureFrame(timestamp: number) {
  if (lastTimestamp > 0) {
    frametimes.push(timestamp - lastTimestamp)
  }
  lastTimestamp = timestamp
  requestAnimationFrame(measureFrame)
}
requestAnimationFrame(measureFrame)

// Expose for Playwright extraction
;(window as any).__FRAMETIMES__ = frametimes
;(window as any).__getFrametimeStats = (clear = true) => {
  const sorted = [...frametimes].sort((a, b) => a - b)
  const len = sorted.length
  const stats = {
    count: len,
    p50: sorted[Math.floor(len * 0.5)] ?? 0,
    p99: sorted[Math.floor(len * 0.99)] ?? 0,
    p999: sorted[Math.floor(len * 0.999)] ?? 0,
    max: sorted[len - 1] ?? 0,
    dropped: sorted.filter((t) => t > 33.33).length,
  }
  if (clear) frametimes.length = 0
  return stats
}
```

### Option 2: Long Animation Frames API (Chrome 123+)

```typescript
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    frametimes.push(entry.duration)
  }
})
observer.observe({ type: 'long-animation-frame', buffered: true })
```

## Benchmark Script Pattern

```bash
#!/bin/bash
# autoresearch.sh — Visual performance benchmark
set -e

URL="${1:-http://localhost:5173}"
WARMUP_FRAMES=60      # Skip first 60 frames (shader compilation, buffer alloc)
MEASURE_FRAMES=300     # Collect 300 frames (~5 seconds at 60fps)
RUNS=3

results=()

for i in $(seq 1 $RUNS); do
  # Run Playwright frametime collection
  node scripts/collect-frametimes.js "$URL" "$WARMUP_FRAMES" "$MEASURE_FRAMES" > frametime-run.log 2>&1
  p999=$(grep "^METRIC p999_frametime_ms=" frametime-run.log | cut -d= -f2)
  results+=("$p999")
done

# Sort and take median
sorted=($(printf '%s\n' "${results[@]}" | sort -n))
median=${sorted[1]}
echo "METRIC p999_frametime_ms=$median"
```

### Playwright Frametime Collector

```javascript
// scripts/collect-frametimes.js
const { chromium } = require('playwright')

const [, , url, warmupStr, measureStr] = process.argv
const WARMUP = parseInt(warmupStr) || 60
const MEASURE = parseInt(measureStr) || 300

;(async () => {
  const browser = await chromium.launch({
    args: ['--enable-unsafe-webgpu', '--enable-features=Vulkan', '--disable-gpu-sandbox', '--use-angle=vulkan'],
  })

  const page = await browser.newPage()
  await page.goto(url)
  await page.waitForLoadState('networkidle')

  // Wait for warmup frames
  await page.evaluate(
    (w) =>
      new Promise((resolve) => {
        let count = 0
        function tick() {
          if (++count >= w) return resolve()
          requestAnimationFrame(tick)
        }
        requestAnimationFrame(tick)
      }),
    WARMUP
  )

  // Clear accumulated frametimes from warmup
  await page.evaluate(() => window.__getFrametimeStats(true))

  // Wait for measurement frames
  await page.evaluate(
    (m) =>
      new Promise((resolve) => {
        let count = 0
        function tick() {
          if (++count >= m) return resolve()
          requestAnimationFrame(tick)
        }
        requestAnimationFrame(tick)
      }),
    MEASURE
  )

  // Extract stats
  const stats = await page.evaluate(() => window.__getFrametimeStats(false))

  // Take screenshot for visual verification
  await page.screenshot({ path: 'autoresearch-screenshot.png', fullPage: false })

  await browser.close()

  // Output metric
  console.log(`METRIC p999_frametime_ms=${stats.p999.toFixed(2)}`)
  console.log(`METRIC p99_frametime_ms=${stats.p99.toFixed(2)}`)
  console.log(`METRIC p50_frametime_ms=${stats.p50.toFixed(2)}`)
  console.log(`METRIC dropped_frames=${stats.dropped}`)
  console.log(`frames_collected=${stats.count}`)
})()
```

## Vite HMR Integration

The agent does **not** need to restart the server between iterations. Vite HMR handles it:

1. Agent edits a `.ts`, `.wgsl`, `.glsl`, or `.wasm` source file
2. Vite detects the change and pushes a hot update to the browser
3. Playwright waits for HMR to settle before measuring:

```javascript
// After edit, wait for HMR update + settle
await page
  .waitForFunction(
    () => {
      // Vite sets this on HMR update
      return document.querySelector('[data-vite-hmr-pending]') === null
    },
    { timeout: 10000 }
  )
  .catch(() => {})
// Additional settle time for GPU pipeline recompilation
await page.waitForTimeout(1000)
```

**If HMR breaks** (full page reload required — common with WASM changes), the script detects and handles it:

```javascript
page.on('load', () => {
  // Full reload happened — re-inject warmup wait
  hmrBroke = true
})
```

## Visual Verification: Agent Sees Its Work

After each iteration, the agent should **view the screenshot** to catch visual regressions the metric won't:

- Blank/black canvas (shader compilation failure)
- Texture corruption or Z-fighting
- Missing geometry or UI overlay
- Infinite canvas zoom/pan broken

**Protocol:** After extracting the metric, use `look_at` on `autoresearch-screenshot.png` with objective "Check for visual regressions: blank canvas, texture corruption, missing geometry, broken UI overlays." If the visual check fails, treat as a CRASH even if the metric improved.

## Scope Guidance

| Layer        | Typical Files                              | Risk |
| ------------ | ------------------------------------------ | ---- |
| Shaders      | `*.wgsl`, `*.glsl`, `*.frag`, `*.vert`     | High |
| WASM         | `*.rs` (compiled to WASM), `*.wat`         | High |
| Render loop  | `renderer.ts`, `pipeline.ts`, `scene.ts`   | Med  |
| Canvas logic | `canvas.ts`, `viewport.ts`, `transform.ts` | Med  |
| UI overlay   | `overlay.ts`, `hud.ts`, `controls.ts`      | Low  |
| Data prep    | `geometry.ts`, `buffers.ts`, `mesh.ts`     | Low  |

**Start with the render loop and data prep** — buffer management, draw call batching, and uniform updates are usually the lowest-risk, highest-impact changes.

## High-Impact Optimization Patterns

Ordered by typical impact for WebGPU/canvas workloads:

1. **Draw call batching** — merge small draws into instanced or indirect draws. Reducing draw calls from 1000→50 can 10x frametime.
2. **Buffer reuse / ring buffers** — allocating GPU buffers per frame is the #1 WebGPU perf killer. Use a ring buffer or pool.
3. **Frustum/occlusion culling** — skip off-screen geometry on infinite canvases. Spatial index (quadtree) for 2D.
4. **Shader compilation caching** — `createRenderPipelineAsync` to avoid blocking. Pre-warm shaders on load.
5. **Reduce overdraw** — sort opaque back-to-front, use depth test, minimize blending passes.
6. **Mipmap / LOD** — on infinite canvases, distant content should use lower LOD.
7. **Compute shader offload** — move CPU-side transforms (matrix math, particle updates) to compute shaders.
8. **requestAnimationFrame discipline** — ensure exactly one rAF loop; multiple loops fight for the frame budget.
9. **Minimize JS↔GPU data transfer** — batch uniform updates, use mapped buffer ranges, avoid readback.
10. **Web Worker offload** — move non-GPU computation (spatial indexing, collision, physics) off the main thread.

## What Typically Doesn't Work

- **Splitting one render pass into multiple** — pass transitions are expensive on GPU
- **Over-tessellation** — more triangles ≠ better quality past a threshold, but costs linearly
- **Synchronous buffer reads** (`mapAsync` + `getMappedRange` in the render loop) — blocks everything
- **Canvas `getContext('2d')` mixed with WebGPU** — context conflicts, forced reallocation
- **Double-buffering textures that don't need it** — wastes GPU memory, increases latency

## Guard Command

The guard ensures the app still builds and renders:

```bash
# Build check
pnpm build > /dev/null 2>&1

# Quick smoke test: can Playwright load the page and get >0 frames?
node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-webgpu'] });
  const page = await browser.newPage();
  await page.goto('${URL:-http://localhost:5173}');
  await page.waitForLoadState('networkidle');
  const ok = await page.evaluate(() => typeof window.__getFrametimeStats === 'function');
  await browser.close();
  if (!ok) { console.error('Frametime collector not found'); process.exit(1); }
})();
"
```

## Noise Handling

GPU benchmarks are inherently noisy (thermal throttling, OS scheduling, compositor interference). Mitigations:

1. **3 runs, take median** — baked into the benchmark script
2. **Warmup frames** — skip the first 60 frames (shader compilation, texture uploads)
3. **Noise floor: require >8% improvement** — GPU timings typically vary ±5% between runs
4. **Close other GPU-heavy apps** — browser tabs, video players, compositors
5. **Pin GPU clock if possible** — `nvidia-smi -lgc` or `intel_gpu_frequency --set`
