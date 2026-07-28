# Testing Anti-Patterns

Common mistakes that make tests unreliable or unmaintainable.

## Testing Implementation Details

**Bad**: Testing internal methods or state

```javascript
test('uses cache internally', () => {
  const service = new UserService()
  service.getUser(1)
  expect(service._cache.has(1)).toBe(true) // Implementation detail!
})
```

**Good**: Test behavior through public interface

```javascript
test('returns same user on repeated calls', async () => {
  const service = new UserService()
  const user1 = await service.getUser(1)
  const user2 = await service.getUser(1)
  expect(user1).toBe(user2) // Behavior, not implementation
})
```

## Flaky Tests

Tests that sometimes pass, sometimes fail.

**Causes**:

- Timing dependencies (`setTimeout`, race conditions)
- Shared state between tests
- External service dependencies
- Random data without fixed seeds

**Fix**: Use condition-based waiting, isolate tests, mock externals.

## Over-Mocking

**Bad**: Mocking everything

```javascript
test('creates user', () => {
  jest.mock('./database')
  jest.mock('./validator')
  jest.mock('./emailer')
  // Test is now just testing your mocks
})
```

**Good**: Mock only boundaries (network, database, clock)

## Test Duplication

**Bad**: Copy-pasting test code

```javascript
test('admin can delete', () => {
  /* 50 lines */
})
test('owner can delete', () => {
  /* same 50 lines with one change */
})
```

**Good**: Use parameterized tests or shared helpers

## Assertion-Free Tests

**Bad**: No assertions

```javascript
test('does something', () => {
  doSomething() // No expect()!
})
```

Every test must assert something meaningful.

## Giant Tests

**Bad**: Testing everything in one test

```javascript
test('user flow', () => {
  // 200 lines testing signup, login, profile, logout
})
```

**Good**: One concept per test, descriptive names
