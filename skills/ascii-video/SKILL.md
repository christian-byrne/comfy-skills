---
name: ascii-video
description: 'Production pipeline for ASCII art video. Supports video-to-ASCII conversion, audio-reactive visuals, generative scenes, and TTS narration. Use when asked to create ASCII videos, convert video to ASCII, or make terminal-based video art.'
interaction: autonomous
type: leaf
---

# ASCII Video Production Pipeline

Create ASCII art videos from existing footage or generate original ASCII animations.

## Prerequisites

```bash
pip install numpy scipy pillow
# Also needs: ffmpeg
# macOS: brew install ffmpeg
# Linux: apt install ffmpeg
```

## Modes

| Mode           | Description                                    |
| -------------- | ---------------------------------------------- |
| Video-to-ASCII | Convert existing video to ASCII representation |
| Audio-reactive | Visuals driven by audio input                  |
| Generative     | Procedural ASCII scenes and patterns           |
| Hybrid         | Mix video conversion with generative overlays  |
| Lyrics/text    | Animated text synced to audio                  |
| TTS narration  | Text-to-speech with visual accompaniment       |

## Pipeline

```
INPUT → ANALYZE → SCENE_FN → TONEMAP → SHADE → ENCODE
```

1. **INPUT** — Video file, audio file, or parameters for generation
2. **ANALYZE** — Extract frames (video) or audio features (reactive)
3. **SCENE_FN** — Generate ASCII frame content per frame
4. **TONEMAP** — Map pixel brightness to ASCII character ramp
5. **SHADE** — Apply character set and optional ANSI colors
6. **ENCODE** — Render to video via ffmpeg

## ASCII Character Ramps

```python
# Light to dark (standard)
RAMP = " .:-=+*#%@"

# Extended
RAMP_EXT = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

# Block characters (highest contrast)
RAMP_BLOCK = " ░▒▓█"
```

## Video to ASCII

```python
import subprocess
import numpy as np
from PIL import Image
import io

def video_to_ascii(video_path, width=120, fps=15):
    """Extract frames and convert to ASCII."""
    cmd = [
        'ffmpeg', '-i', video_path,
        '-vf', f'fps={fps},scale={width}:-1',
        '-f', 'image2pipe', '-vcodec', 'rawvideo', '-pix_fmt', 'gray', '-'
    ]
    # Process frames...
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    # Read frame data, convert each pixel to ASCII char from ramp
```

## Render to Video

```bash
# Render ASCII frames to video with ffmpeg
# 1. Generate frame images (PIL/Pillow with monospace font)
# 2. Encode:
ffmpeg -framerate 30 -i frames/frame_%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4

# Add audio track:
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac -shortest output_with_audio.mp4
```

## Creative Standards

- **First-render excellence** — each frame should look good on its own
- **Per-section variation** — vary character sets, density, and effects across sections
- **Cohesive aesthetics** — maintain consistent style within a piece
- **Frame rate** — 15fps for retro feel, 30fps for smooth, 60fps for fluid
- **Resolution** — 80-120 columns is the sweet spot for readability
