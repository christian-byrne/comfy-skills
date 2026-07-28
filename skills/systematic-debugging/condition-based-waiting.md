# Condition-Based Waiting

Replace arbitrary timeouts with condition polling.

## The Problem

```javascript
// Bad: arbitrary timeout
await delay(5000)
expect(element).toBeVisible()
```

This is flaky:

- Too short: fails on slow machines
- Too long: wastes time on fast machines

## The Solution

Poll for the condition:

```javascript
// Good: wait for condition
await waitFor(() => expect(element).toBeVisible())
```

## Implementation Pattern

```typescript
async function waitFor(
  condition: () => boolean | Promise<boolean>,
  options: { timeout?: number; interval?: number } = {}
) {
  const { timeout = 5000, interval = 100 } = options
  const start = Date.now()

  while (Date.now() - start < timeout) {
    if (await condition()) return
    await delay(interval)
  }

  throw new Error('Condition not met within timeout')
}
```

## Common Use Cases

### Wait for Element

```javascript
await waitFor(() => document.querySelector('.loaded') !== null)
```

### Wait for API

```javascript
await waitFor(async () => {
  const res = await fetch('/health')
  return res.ok
})
```

### Wait for State

```javascript
await waitFor(() => store.getState().isReady)
```

## Best Practices

- Set reasonable max timeout (fail fast if truly broken)
- Use short polling interval (don't miss the condition)
- Add descriptive error message for timeout failures
- Consider exponential backoff for expensive checks
