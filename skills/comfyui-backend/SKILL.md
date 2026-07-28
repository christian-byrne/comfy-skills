---
name: comfyui-backend
description: 'Convention knowledge for ComfyUI backend. Python node system, V3 API patterns, testing, and directory layout.'
type: leaf
---

# ComfyUI Backend Conventions

Repo: `comfyanonymous/ComfyUI` — Python 3.10+ / PyTorch / aiohttp server

## Directory Layout

| Path               | Purpose                                                                  |
| ------------------ | ------------------------------------------------------------------------ |
| `comfy/`           | Core inference engine — model management, samplers, memory, SD pipelines |
| `comfy_api/`       | Versioned node API (`v0_0_1/`, `v0_0_2/`, `latest/`) with `io` module    |
| `comfy_api_nodes/` | Cloud API nodes (BFL, Bria, etc.) using `comfy_api.latest`               |
| `comfy_extras/`    | Built-in extra nodes (post-processing, upscale, etc.)                    |
| `comfy_execution/` | Execution engine, graph traversal, caching                               |
| `api_server/`      | HTTP/WebSocket server routes                                             |
| `app/`             | Application startup and configuration                                    |
| `nodes.py`         | Legacy core node definitions (older `ComfyNodeABC` style)                |
| `tests/`           | Integration tests (pytest, markers: `inference`, `execution`)            |
| `tests-unit/`      | Unit tests (pytest, organized by module)                                 |

## Node Definition — V3 API (preferred for new nodes)

```python
from comfy_api.latest import ComfyExtension, io

class MyNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="MyNodeId",        # unique, stable identifier
            display_name="My Node",
            category="image/transform",
            inputs=[
                io.Image.Input("image"),
                io.Float.Input("strength", default=1.0, min=0.0, max=1.0, step=0.01),
            ],
            outputs=[
                io.Image.Output(),
            ],
        )

    @classmethod
    def execute(cls, image, strength):
        result = do_something(image, strength)
        return io.NodeOutput(result)
```

- `node_id` must be globally unique and never change after release
- `execute` is a **classmethod** — no instance state
- Import from `comfy_api.latest`, not version-specific modules
- Helper utilities in `comfy_api_nodes/util.py` (download, polling, tensor conversion)

## Legacy Node Pattern (nodes.py — avoid for new code)

Uses `ComfyNodeABC` with `INPUT_TYPES`, `RETURN_TYPES`, `FUNCTION` class attributes. Still present in `nodes.py` but new nodes should use V3 API.

## Linting & Formatting

- **Ruff** for linting (`pyproject.toml` config) — select rules: `N805`, `S307`, `S102`, `E`, `T`, `W`, `F`
- Line length not enforced (`E501` ignored)
- No formatter enforced globally — match surrounding file style

## Testing

```bash
# All tests
pytest

# Skip slow inference tests
pytest -m "not inference"

# Unit tests only
pytest tests-unit/
```

- `pytest.ini` sets `pythonpath = .` and `addopts = -s`
- Integration tests may need GPU and models — use `@pytest.mark.inference`
- Unit test dirs mirror source: `tests-unit/comfy_test/`, `tests-unit/comfy_extras_test/`

## Key Patterns

- **Tensors are BHWC** (batch, height, width, channels) for images — not BCHW
- **`folder_paths.py`** manages all model/input/output directory resolution
- **`comfy.model_management`** handles device placement, memory, interrupts
- **`node_helpers.py`** has shared utilities like `image_alpha_fix`
- All node files in `comfy_extras/` are auto-discovered — just create the file

## Skill Combos

When working in this repo, load companion skills based on what you're touching:

| File pattern              | Also load skill           | Why                         |
| ------------------------- | ------------------------- | --------------------------- |
| Bug investigation         | `systematic-debugging`    | 4-phase root cause analysis |
| `tests/` or `tests-unit/` | `test-driven-development` | Red-green-refactor cycle    |

For refactoring tasks, make changes in small, safely-verified steps with tests passing before and after each step.

## Commit Messages

Use conventional format: `feat:`, `fix:`, `test:`. Never mention AI/Claude.
