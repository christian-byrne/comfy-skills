---
name: powerpoint
description: 'Create, read, and edit PowerPoint (.pptx) presentations. Supports reading via markitdown, editing via XML manipulation, creating from scratch via pptxgenjs. Includes design guidance for professional slides. Use when asked to create presentations, edit slides, or work with PPTX files.'
interaction: autonomous
type: leaf
---

# PowerPoint / PPTX

Work with `.pptx` files — reading, editing, and creating presentations.

## Reading Presentations

### Quick Content View (markitdown)

```bash
pip install markitdown 2>/dev/null
markitdown presentation.pptx
```

### Visual Thumbnail Overview

```bash
# Convert to PDF then to images
libreoffice --headless --convert-to pdf presentation.pptx
pdftoppm -png presentation.pdf slide
# Then use look_at tool on generated images
```

### Raw XML Inspection

```bash
mkdir unpacked && cd unpacked
unzip ../presentation.pptx
# Slides are in ppt/slides/slide1.xml, slide2.xml, etc.
```

## Creating Presentations (pptxgenjs)

Use Node.js with pptxgenjs for creating from scratch (requires Node.js 18+):

```bash
npm install pptxgenjs
```

```javascript
const pptxgen = require('pptxgenjs')
const pres = new pptxgen()

// Master slide / branding
pres.defineSlideMaster({
  title: 'MAIN',
  background: { color: 'FFFFFF' },
  objects: [{ rect: { x: 0, y: 0, w: '100%', h: 0.5, fill: { color: '1a1a2e' } } }],
})

// Title slide
let slide = pres.addSlide()
slide.addText('Presentation Title', {
  x: 0.5,
  y: 1.5,
  w: 9,
  h: 1.5,
  fontSize: 36,
  fontFace: 'Helvetica',
  bold: true,
  color: '1a1a2e',
})
slide.addText('Subtitle or date', {
  x: 0.5,
  y: 3.0,
  w: 9,
  h: 0.8,
  fontSize: 18,
  color: '666666',
})

// Content slide
let slide2 = pres.addSlide()
slide2.addText('Section Title', {
  x: 0.5,
  y: 0.3,
  w: 9,
  h: 0.8,
  fontSize: 24,
  bold: true,
  color: '1a1a2e',
})
slide2.addText(
  [
    { text: '• First point\n', options: { fontSize: 16 } },
    { text: '• Second point\n', options: { fontSize: 16 } },
    { text: '• Third point', options: { fontSize: 16 } },
  ],
  { x: 0.5, y: 1.5, w: 8, h: 3 }
)

pres.writeFile({ fileName: 'output.pptx' })
```

## Editing Existing Presentations

Workflow: unpack → edit XML → repack

```bash
# Unpack
mkdir work && cd work
unzip ../original.pptx

# Edit slide XML (e.g., change text)
# Slides are in ppt/slides/slide*.xml
# Text runs are in <a:r><a:t>text here</a:t></a:r>

# Repack
zip -r ../modified.pptx . -x ".*"
```

For Python-based editing:

```bash
pip install python-pptx
```

```python
from pptx import Presentation
prs = Presentation('input.pptx')
for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                print(para.text)
prs.save('output.pptx')
```

## Brand Styles

Pick a brand style upfront — apply it consistently across all slides.

| Style                                      | Colors                                               | Typography             | Transitions      | Use For                        |
| ------------------------------------------ | ---------------------------------------------------- | ---------------------- | ---------------- | ------------------------------ |
| **Tech Keynote** (Apple/Tesla)             | Black `#000000`, white, blue `#0071E3`               | SF Pro 72-96pt titles  | Push/Fade 0.6s   | Product launches, demos        |
| **Corporate Professional** (Microsoft/IBM) | Navy `#003366`, steel blue `#0078D4`, gray `#F3F2F1` | Segoe UI 54-72pt       | Morph/Fade 0.8s  | Business reports, proposals    |
| **Creative Bold** (Google/Airbnb)          | Bright primaries, gradients                          | Montserrat 64-84pt     | Zoom/Reveal 0.5s | Marketing, design showcases    |
| **Financial Elite** (Goldman/McKinsey)     | Charcoal `#2C3E50`, gold `#D4AF37`, white            | Garamond/Georgia serif | Subtle Fade 0.4s | Investor decks, financials     |
| **Startup Pitch** (YC/500)                 | High-contrast black/white + brand accent             | Inter/Roboto           | Quick Push 0.3s  | Fundraising, accelerator demos |

Set via frontmatter:

```yaml
---
style: tech-keynote
accent-color: '#0071E3'
animations: minimal # minimal, moderate, full
colors:
  primary: '#003366'
  accent: '#0078D4'
---
```

## Slide Type Detection (Markdown → Slide)

```markdown
# Title → title_slide (hero treatment, 96pt, brand gradient bg)

## Section → chapter_intro (full-screen background, 84pt centered)

### Key points → key_message_slide (1-3 points)

- Bullets → bullet_hierarchy_slide
  > Quote → quote_slide (large, impactful)
  > ![image] → full_bleed_image (auto-crop 16:9, 20% gradient overlay if text)
  > | table | → data_visualization (auto-convert to chart if numeric)
  > **94%** or $2M → key_metrics_dashboard (144pt metric, count-up animation 1.2s)
  > === → chapter_intro section divider (fade-to-black 1.0s)
```

**Content → template mapping:**

```
Opening/Closing     → title_slide, thank_you_slide
New section         → chapter_intro
Key points (1-3)    → key_metrics_dashboard
Comparison          → before_after_comparison, chart_comparison
Process/Timeline    → process_flow, timeline_slide
Team                → team_introduction
Data                → data_table_slide, chart layouts
Mixed content       → two_column_text, three_column_layout
Full image          → full_image_slide
Quote               → quote_testimonial
```

## Design Guidance

### Color Palettes (custom)

| Name      | Primary   | Secondary | Accent    | Background |
| --------- | --------- | --------- | --------- | ---------- |
| Corporate | `#1a1a2e` | `#16213e` | `#0f3460` | `#ffffff`  |
| Modern    | `#2d3436` | `#636e72` | `#00b894` | `#f5f5f5`  |
| Warm      | `#2d3436` | `#d63031` | `#fdcb6e` | `#ffffff`  |
| Cool      | `#0c2461` | `#0a3d62` | `#3c6382` | `#f8f9fa`  |

### Typography Scale

| Element        | Size    | Weight   |
| -------------- | ------- | -------- |
| Hero title     | 72-96pt | Bold     |
| Slide title    | 44-54pt | Semibold |
| Section header | 24-36pt | Bold     |
| Body text      | 24-28pt | Regular  |
| Caption/note   | 18-20pt | Light    |

### Spacing System

```
Gutter (edge margin): 100-120px
Title margin-bottom:  60-80px
Section spacing:      40-60px
Paragraph spacing:    24-32px
Bullet indent:        40px
```

### Layout Rules

- **Max 6 bullet points per slide** — less is more
- **One idea per slide** — if you need "and", split it
- **2/3 rule** — leave 1/3 of the slide as breathing room
- **Consistent margins** — 0.5" (100px) on all sides minimum
- **Left-align body text** — center only for titles and single lines
- **No walls of text** — if it's more than 6 lines, it's a document not a slide
- **Aim for 1 slide per minute** of presentation time
- **Accessibility** — maintain 4.5:1 contrast ratio for all text

### Anti-Patterns

- ❌ Never use accent lines under titles — hallmark of AI-generated slides
- ❌ No gradients on text
- ❌ No more than 2 font families per deck (3 absolute max)
- ❌ No clip art — use icons or real photos
- ❌ Don't read your slides verbatim
- ❌ Avoid Ferris Wheel, Curtains, Dissolve, Origami transitions — unprofessional

## Transitions & Animations

### Transition Tiers

| Tier                  | Transitions                               | When                 |
| --------------------- | ----------------------------------------- | -------------------- |
| **1 — Always safe**   | Fade (0.6s), Push (0.4s), Morph (0.8s)    | Use liberally        |
| **2 — Use sparingly** | Zoom (0.5s), Reveal (0.6s), Wipe (0.5s)   | Special moments only |
| **3 — Never use**     | Ferris Wheel, Curtains, Dissolve, Origami | —                    |

**Rules:** 1-2 transition types max per deck. Never more than 3 animated elements per slide.

### Animation Best Practices

- **Entrance**: Fade In for text (0.4s); stagger bullets with 0.3s delay between each
- **Emphasis ("AHA!" moment)**: Pick 1-2 critical slides per deck, apply single Pulse/Grow (0.8-1.0s), fires once
- **Images**: Wipe or Fade In (0.6s), from bottom direction
- **Exit**: Fade Out only (0.3s)
- **Metrics**: Count-up animation (1.2s) for key numbers auto-detected in bold (`**94%**`, `$2.4M`)

## Office-PowerPoint-MCP-Server (Alternative to pptxgenjs)

For 25+ professional templates with intelligent mapping, use the MCP server:

```bash
# Install
npx @smithery/cli install @gongrzhe/office-powerpoint-mcp-server

# Or local
pip install python-pptx pillow pyyaml
```

The MCP server provides template-based creation with all brand styles pre-configured.

## QA Verification

```bash
# Content QA — check all text is correct
markitdown output.pptx

# Visual QA — convert to images and inspect
libreoffice --headless --convert-to pdf output.pptx
pdftoppm -png output.pdf slide-preview
# Then use look_at tool on the PNGs
```
