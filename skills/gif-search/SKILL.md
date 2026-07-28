---
name: gif-search
description: 'Search and download GIFs from Tenor using curl. No dependencies beyond curl and jq. Use when asked to find GIFs, search for reaction GIFs, or download animated images.'
interaction: autonomous
type: leaf
---

# GIF Search — Tenor API

Search and download GIFs from Tenor. Only needs `curl` and `jq`.

## Prerequisites

Get a free Tenor API key from [Google Cloud Console](https://console.cloud.google.com/) → APIs → Tenor API.

Set: `export TENOR_API_KEY="your-key-here"`

## Commands

### Search GIFs

```bash
curl -s "https://tenor.googleapis.com/v2/search?q=thumbs+up&key=$TENOR_API_KEY&limit=5" | jq '.results[] | {title: .title, url: .media_formats.gif.url}'
```

### Get Top Result URL

```bash
curl -s "https://tenor.googleapis.com/v2/search?q=celebration&key=$TENOR_API_KEY&limit=1" | jq -r '.results[0].media_formats.gif.url'
```

### Download Top Result

```bash
URL=$(curl -s "https://tenor.googleapis.com/v2/search?q=celebration&key=$TENOR_API_KEY&limit=1" | jq -r '.results[0].media_formats.gif.url')
curl -o celebration.gif "$URL"
```

### Get Multiple Formats

```bash
curl -s "https://tenor.googleapis.com/v2/search?q=hello&key=$TENOR_API_KEY&limit=1" | jq '.results[0].media_formats | keys'
```

## Available Formats

| Format    | Description      |
| --------- | ---------------- |
| `gif`     | Full quality GIF |
| `tinygif` | Compressed GIF   |
| `mp4`     | MP4 video        |
| `tinymp4` | Compressed MP4   |
| `webm`    | WebM video       |
| `nanogif` | Tiny preview GIF |

## API Parameters

| Parameter       | Description                             |
| --------------- | --------------------------------------- |
| `q`             | Search query                            |
| `key`           | API key                                 |
| `limit`         | Results count (default 20)              |
| `media_filter`  | Filter formats: `gif`, `tinygif`, `mp4` |
| `contentfilter` | Safety: `off`, `low`, `medium`, `high`  |
| `locale`        | Language: `en_US`, `es`, etc.           |
