---
name: p5js
description: 'Create interactive and generative visual art using p5.js. Supports generative art, data visualization, interactive experiences, animation, and 3D scenes. Self-contained HTML files. Use when asked to create generative art, creative coding, interactive visualizations, or p5.js sketches.'
interaction: autonomous
type: leaf
---

# p5.js — Creative Coding & Generative Art

Create interactive and generative visual art as self-contained HTML files.

## Quick Start

Every p5.js project is a single HTML file:

```html
<!DOCTYPE html>
<html>
  <head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.0/p5.min.js"></script>
  </head>
  <body>
    <script>
      function setup() {
        createCanvas(800, 600)
        background(20)
      }

      function draw() {
        // Animation loop — runs 60fps
        fill(random(255), random(255), random(255), 50)
        noStroke()
        ellipse(mouseX, mouseY, 30, 30)
      }
    </script>
  </body>
</html>
```

## Modes

| Mode                      | Description                     |
| ------------------------- | ------------------------------- |
| Generative art            | Algorithmic visual compositions |
| Data visualization        | Interactive charts and graphs   |
| Interactive experience    | Mouse/keyboard-driven visuals   |
| Animation/motion graphics | Frame-by-frame animation        |
| 3D scene                  | WebGL-based 3D rendering        |
| Image processing          | Pixel manipulation, filters     |
| Audio-reactive            | Sound-driven visuals (p5.sound) |

## Key Patterns

### Color (HSB mode recommended)

```javascript
colorMode(HSB, 360, 100, 100, 100)
fill(200, 80, 90) // hue, saturation, brightness
stroke(0, 0, 100) // white
```

### Seeded Randomness (reproducible)

```javascript
randomSeed(42)
noiseSeed(42)
let x = random(width)
let n = noise(frameCount * 0.01) // Perlin noise, 0-1
```

### Multi-Octave Noise

```javascript
function fbm(x, y, octaves = 4) {
  let value = 0,
    amplitude = 1,
    frequency = 1,
    total = 0
  for (let i = 0; i < octaves; i++) {
    value += noise(x * frequency, y * frequency) * amplitude
    total += amplitude
    amplitude *= 0.5
    frequency *= 2
  }
  return value / total
}
```

### Layers (createGraphics)

```javascript
let bg, fg
function setup() {
  createCanvas(800, 600)
  bg = createGraphics(800, 600)
  fg = createGraphics(800, 600)
  bg.background(20)
}
function draw() {
  // Draw to layers independently
  fg.clear()
  fg.ellipse(mouseX, mouseY, 50)
  image(bg, 0, 0)
  image(fg, 0, 0)
}
```

### WebGL (3D)

```javascript
function setup() {
  createCanvas(800, 600, WEBGL)
}
function draw() {
  background(0)
  rotateX(frameCount * 0.01)
  rotateY(frameCount * 0.02)
  normalMaterial()
  box(100)
}
```

## Exporting

### Static Image

```javascript
function keyPressed() {
  if (key === 's') saveCanvas('output', 'png')
}
```

### Animation (via CCapture.js)

```html
<script src="https://cdn.jsdelivr.net/npm/ccapture.js@1.1.0/build/CCapture.all.min.js"></script>
<script>
  let capturer = new CCapture({ format: 'webm', framerate: 60 })
  function setup() {
    createCanvas(800, 600)
    capturer.start()
  }
  function draw() {
    // ... your art ...
    capturer.capture(document.querySelector('canvas'))
    if (frameCount >= 300) {
      capturer.stop()
      capturer.save()
      noLoop()
    }
  }
</script>
```

### Headless Export (Puppeteer)

```javascript
// Add noLoop() after drawing is complete, then:
// puppeteer screenshot the canvas element
```

## Performance Tips

- Use `noLoop()` for static pieces — no need to redraw 60fps
- Limit particle counts to ~5000 for smooth 60fps
- Use `createGraphics()` for persistent layers instead of redrawing everything
- Prefer `noStroke()` when stroke isn't needed — significant perf gain
- Use `pixelDensity(1)` on retina displays for faster rendering
