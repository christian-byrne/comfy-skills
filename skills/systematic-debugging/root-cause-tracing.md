# Root Cause Tracing

Techniques for tracing bugs back to their source.

## The Backward Trace Method

Start at the symptom, work backward:

1. **Symptom**: What's the observable problem?
2. **Immediate cause**: What directly caused the symptom?
3. **Prior cause**: What caused that cause?
4. **Repeat**: Keep going until you find the root

## Example Trace

```
Symptom: User sees "undefined" in the UI
↓
Immediate cause: Component renders user.name, but user is undefined
↓
Prior cause: API call returned null instead of user object
↓
Prior cause: Backend query found no matching user
↓
Root cause: User ID from session was stale after password reset
```

## Tracing Techniques

### Add Logging

```javascript
console.log('getData called with:', params)
const result = await fetch(url)
console.log('getData returned:', result)
```

### Use Debugger

Set breakpoints and inspect:

- Variable values at each step
- Call stack at failure point
- State before and after operations

### Binary Search

If the bug appeared recently:

1. Find a known-good commit
2. Find the broken commit
3. Binary search to find the exact commit that broke it

### Rubber Duck

Explain the code path out loud:

- What should happen at each step?
- What actually happens?
- Where does expectation diverge from reality?

## Common Root Causes

- **Timing**: Race conditions, missing awaits
- **State**: Stale data, incorrect initialization
- **Boundaries**: Off-by-one, null/undefined checks
- **Assumptions**: Code assumes something that isn't always true
