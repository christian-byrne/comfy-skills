# Defense in Depth

Add validation at multiple layers to catch bugs early.

## The Principle

Don't rely on a single check. Add validation at every boundary.

## Layer Examples

### Input Validation

```typescript
function processUser(user: User) {
  if (!user) throw new Error('User required')
  if (!user.id) throw new Error('User ID required')
  // Now proceed safely
}
```

### Database Constraints

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### API Validation

```typescript
app.post('/users', validateBody(userSchema), (req, res) => {
  // Body is guaranteed to match schema
})
```

### Type System

```typescript
// Use types to make invalid states unrepresentable
type ValidatedEmail = string & { __brand: 'email' }

function sendEmail(to: ValidatedEmail) {
  // Can only be called with validated email
}
```

## When to Add Defense

After fixing any bug, ask:

1. Where else could this fail?
2. What validation would have caught this earlier?
3. Can I make this failure impossible through types/schema?

## Defense Layers

1. **Compile time**: Types, schemas
2. **Startup time**: Config validation
3. **Request time**: Input validation
4. **Runtime**: Assertions, invariant checks
5. **Database**: Constraints, triggers
