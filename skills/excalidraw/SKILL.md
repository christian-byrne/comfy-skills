---
name: excalidraw
description: 'Create hand-drawn style diagrams by writing Excalidraw JSON files. Produces .excalidraw files that can be drag-and-dropped onto excalidraw.com. Use when the user wants hand-drawn diagrams, architecture sketches, or whiteboard-style visuals.'
interaction: autonomous
type: leaf
---

# Excalidraw Diagram Creator

Create hand-drawn style diagrams by writing `.excalidraw` JSON files directly. No browser or API needed — files can be drag-and-dropped onto excalidraw.com to view/edit.

## File Structure

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "agent",
  "elements": [],
  "appState": {
    "viewBackgroundColor": "#ffffff",
    "gridSize": 20
  }
}
```

## Element Types

### Rectangle

```json
{
  "type": "rectangle",
  "id": "rect1",
  "x": 100,
  "y": 100,
  "width": 200,
  "height": 80,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#a5d8ff",
  "fillStyle": "hachure",
  "strokeWidth": 2,
  "roughness": 1,
  "roundness": { "type": 3 }
}
```

### Ellipse

```json
{
  "type": "ellipse",
  "id": "ell1",
  "x": 400,
  "y": 100,
  "width": 150,
  "height": 100,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#b2f2bb",
  "fillStyle": "hachure"
}
```

### Diamond

```json
{
  "type": "diamond",
  "id": "dia1",
  "x": 200,
  "y": 300,
  "width": 120,
  "height": 120,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#ffec99",
  "fillStyle": "hachure"
}
```

### Text (Standalone)

```json
{
  "type": "text",
  "id": "txt1",
  "x": 100,
  "y": 50,
  "text": "Hello World",
  "fontSize": 20,
  "fontFamily": 1,
  "textAlign": "center",
  "strokeColor": "#1e1e1e"
}
```

### Labeled Shape (Container Binding)

⚠️ **NEVER use a `"label"` property directly on shapes.** Use container binding instead:

```json
[
  {
    "type": "rectangle",
    "id": "container1",
    "x": 100,
    "y": 100,
    "width": 200,
    "height": 80,
    "boundElements": [{ "id": "label1", "type": "text" }]
  },
  {
    "type": "text",
    "id": "label1",
    "x": 130,
    "y": 125,
    "text": "My Label",
    "fontSize": 16,
    "textAlign": "center",
    "containerId": "container1",
    "width": 140,
    "height": 25
  }
]
```

### Arrow

```json
{
  "type": "arrow",
  "id": "arr1",
  "x": 300,
  "y": 140,
  "width": 100,
  "height": 0,
  "points": [
    [0, 0],
    [100, 0]
  ],
  "strokeColor": "#1e1e1e",
  "strokeWidth": 2,
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

### Arrow with Bindings (Connected to Shapes)

```json
{
  "type": "arrow",
  "id": "arr2",
  "x": 300,
  "y": 140,
  "width": 100,
  "height": 0,
  "points": [
    [0, 0],
    [100, 0]
  ],
  "startBinding": { "elementId": "rect1", "focus": 0, "gap": 5, "fixedPoint": null },
  "endBinding": { "elementId": "rect2", "focus": 0, "gap": 5, "fixedPoint": null }
}
```

Remember to add the arrow to each bound element's `boundElements` array.

## Sizing Guidelines

| Element                  | Recommended Size |
| ------------------------ | ---------------- |
| Standard box             | 200×80           |
| Small box                | 120×60           |
| Large container          | 300×150          |
| Database cylinder        | 120×80 (ellipse) |
| Spacing between elements | 40-60px          |
| Arrow length             | 60-100px         |
| Font size (labels)       | 16-20            |
| Font size (titles)       | 24-28            |

## Color Palette

| Purpose          | Color     |
| ---------------- | --------- |
| Blue (primary)   | `#a5d8ff` |
| Green (success)  | `#b2f2bb` |
| Yellow (warning) | `#ffec99` |
| Red (error)      | `#ffc9c9` |
| Purple (special) | `#d0bfff` |
| Gray (neutral)   | `#dee2e6` |
| Stroke           | `#1e1e1e` |

## Z-Order

Elements are rendered in array order — later elements appear on top. Place arrows AFTER the shapes they connect.

## Fill Styles

- `"hachure"` — hand-drawn cross-hatching (default, most "Excalidraw" feel)
- `"cross-hatch"` — denser cross-hatching
- `"solid"` — solid fill
- `"dots"` — dot pattern (reserved, not widely supported)

## Roughness

- `0` — clean lines
- `1` — slightly rough (default, recommended)
- `2` — very rough/sketchy

## Workflow

1. Plan the diagram layout on a grid
2. Create shapes with IDs
3. Create text labels with `containerId` bindings
4. Create arrows with start/end bindings
5. Add bound element references to all connected shapes
6. Save as `diagram-name.excalidraw`
7. Verify: drag-and-drop onto excalidraw.com
