---
name: twitter
description: 'Post tweets, threads, media, and automate X/Twitter via inference.sh belt CLI. Apps: x/post-tweet, x/post-create (with media), x/post-like, x/post-retweet, x/dm-send, x/user-follow. Use for: twitter automation, tweet posting, thread creation, X API, twitter bot, social media automation, schedule tweets, engagement. Triggers: post tweet, tweet automation, twitter thread, x automation, send tweet, twitter post, post to twitter, twitter integration, x post, tweet storm, twitter content'
interaction: autonomous
type: leaf
allowed-tools: Bash(belt *)
synergies:
  domain: [social-media, automation, content]
---

# Twitter/X Automation

Automate Twitter/X via [inference.sh](https://inference.sh) `belt` CLI.

## Prerequisites

```bash
belt login
```

> `belt` is the inference.sh CLI. Install: `npx skills add inference-sh/skills@infsh-cli` or see [inference.sh docs](https://inference.sh/docs).

## Post

| Action          | Command                                                                    |
| --------------- | -------------------------------------------------------------------------- |
| Post tweet      | `belt app run x/post-tweet --input '{"text": "..."}'`                      |
| Post with media | `belt app run x/post-create --input '{"text": "...", "media_url": "..."}'` |
| Delete tweet    | `belt app run x/post-delete --input '{"tweet_id": "..."}'`                 |
| Get tweet       | `belt app run x/post-get --input '{"tweet_id": "..."}'`                    |

## Engage

| Action      | Command                                                                   |
| ----------- | ------------------------------------------------------------------------- |
| Like        | `belt app run x/post-like --input '{"tweet_id": "..."}'`                  |
| Retweet     | `belt app run x/post-retweet --input '{"tweet_id": "..."}'`               |
| Send DM     | `belt app run x/dm-send --input '{"recipient_id": "...", "text": "..."}'` |
| Follow user | `belt app run x/user-follow --input '{"username": "..."}'`                |
| Get profile | `belt app run x/user-get --input '{"username": "..."}'`                   |

## Threads

Post the hook first, then reply-chain each subsequent tweet immediately.

### Structure

```
Tweet 1 (Hook):     Bold claim or question + "🧵"
Tweet 2:            Context / why it matters
Tweets 3–9:         One point per tweet, numbered (3/, 4/, ...)
Tweet 10:           Summary / biggest takeaway
Tweet 11:           CTA — follow, RT, bookmark
```

### Hook formulas

| Type            | Template                                               |
| --------------- | ------------------------------------------------------ |
| Result-led      | "I analyzed 1,000 [X]. Here's what I found:"           |
| Number list     | "10 [topic] tips that [benefit]:"                      |
| Contrarian      | "Unpopular opinion: [bold take]"                       |
| Story opener    | "In [year], I [dramatic event]. Here's what happened:" |
| Surprising stat | "[Stat that seems wrong]. Let me explain:"             |

### Formatting rules

- One idea per tweet — keep each retweetable on its own
- Use `→` for steps/actions, `•` for bullets, `✅`/`❌` for do/don't
- Short sentences + blank lines: pacing drives reading speed
- 280 chars for free accounts; 25,000 chars with Premium

```bash
# Post hook tweet
belt app run x/post-create --input '{
  "text": "I spent 3 years building SaaS products.\n\n10 things I wish someone told me on day 1:\n\n🧵"
}'
```

## Post with AI-generated media

```bash
# 1. Generate image
belt app run falai/flux-dev-lora --input '{"prompt": "sunset over mountains"}' > image.json

# 2. Post with that image
belt app run x/post-create --input '{
  "text": "AI-generated art 🌅",
  "media_url": "<url-from-step-1>"
}'
```

## Common mistakes

| Mistake                  | Fix                                                   |
| ------------------------ | ----------------------------------------------------- |
| Weak hook                | Use hook formulas — bold, specific, curiosity-driving |
| 20+ tweet threads        | Sweet spot is 8–12 tweets                             |
| Multiple ideas per tweet | One idea = one tweet                                  |
| No tweet numbers         | Always number: 1/, 2/, 3/                             |
| No images                | Add visuals to hook + key points                      |
| No CTA                   | End with: RT, follow, or bookmark ask                 |
| Wrong time               | Post during audience's peak hours (8–10 AM, 12–1 PM)  |

## Image specs

| Format      | Dimensions      | Max size |
| ----------- | --------------- | -------- |
| Single      | 1200×675 (16:9) | 5 MB     |
| Two images  | 700×800 each    | 5 MB     |
| Four images | 600×600 each    | 5 MB     |
| GIF         | 1280×1080 max   | 15 MB    |
