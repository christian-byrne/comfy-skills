---
name: comfyui-docs
description: 'Convention knowledge for ComfyUI documentation site (docs.comfy.org). Mintlify-powered, MDX content, bilingual (en/zh-CN).'
type: leaf
---

# ComfyUI Docs Conventions

Repo: `Comfy-Org/docs` — Mintlify docs platform at docs.comfy.org

## Stack

| Layer          | Choice                                     |
| -------------- | ------------------------------------------ |
| Platform       | Mintlify (`mint` v4.x)                     |
| Content format | MDX (`.mdx` files with YAML frontmatter)   |
| Config         | `docs.json` — navigation, theme, tabs      |
| Dev server     | `npx mint dev`                             |
| Languages      | English (root) + Chinese (`zh-CN/` mirror) |

## File Structure

<!-- docs-linter-disable-next-tree -->

```
docs/
├── docs.json              # Navigation config (tabs, groups, pages)
├── index.mdx              # Landing page
├── get_started/           # Getting started guides
├── installation/          # Install guides (desktop, portable, manual)
├── interface/             # UI feature docs
├── tutorials/             # Step-by-step tutorials (by model/technique)
│   ├── basic/
│   ├── video/
│   └── ...
├── development/           # Developer docs (server, core concepts, cloud)
├── custom-nodes/          # Custom node development guides
├── registry/              # Node registry docs
├── specs/                 # JSON specs (workflow, nodedef)
├── api-reference/         # OpenAPI-generated API docs
├── zh-CN/                 # Chinese translations (mirrors en structure)
├── images/                # Screenshots and diagrams
└── public/                # Static assets
```

## Page Frontmatter

Every `.mdx` file must have YAML frontmatter:

```yaml
---
title: 'Page Title'
description: 'Brief description for SEO and navigation'
sidebarTitle: 'Short Nav Title' # optional, shown in sidebar
icon: 'font-awesome-icon-name' # optional
---
```

## Navigation

All pages must be registered in `docs.json` under `navigation.languages[].tabs[].pages`. Pages not listed there won't appear in navigation. Structure:

```json
{
  "tab": "Tab Name",
  "pages": [
    { "group": "Group Name", "pages": ["path/to/page", ...] }
  ]
}
```

- Page paths are relative to repo root, without `.mdx` extension
- Groups can be nested

## Key Conventions

1. **Bilingual**: English content goes in root dirs. Chinese translations mirror the structure under `zh-CN/`. Both must be registered in `docs.json`.
2. **Images**: Store in `images/` directory, reference with relative paths
3. **OpenAPI**: Registry API from `https://api.comfy.org/openapi`, Cloud API from `openapi-cloud.yaml`
4. **Snippets**: Reusable content fragments in `snippets/`
5. **Tutorials are model-organized**: `tutorials/video/wan/`, `tutorials/flux/`, etc.
6. **No build step** — Mintlify handles rendering. Just edit MDX and preview with `npx mint dev`

## Skill Combos

When working in this repo, apply the following depending on what you're touching:

| File pattern        | Guidance                                                           |
| ------------------- | ------------------------------------------------------------------ |
| SEO-related pages   | Apply standard SEO practices: meta tags, structured data, sitemaps |
| Writing new content | Research the topic, then write clearly for the target audience     |
