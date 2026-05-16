# Skill: API Route Standard

## File Location
- `apps/studio/src/app/api/{resource}/route.ts`
- `apps/studio/src/app/api/{resource}/[id]/route.ts`

## Standard Response Shape (ALWAYS)
- **Success**: `{ data: T, meta?: { count, page } }`
- **Error**: `{ error: string, code: string, details?: any }`

## Auth Pattern
```typescript
import { getSession } from '@/lib/auth';

const session = await getSession(req);
if (!session) {
  return Response.json({ error: 'Unauthorized', code: 'UNAUTHORIZED' }, { status: 401 });
}
```

## Redis Pattern
```typescript
import { redis } from '@/lib/redis';

// Keys MUST use NS namespace:
const KEY = `aix:${resource}:${id}`; 
```

## Rate Limiting Pattern
```typescript
import { checkRateLimit } from '@/lib/mcp-router';

const allowed = await checkRateLimit(session.userId, 'api-call');
if (!allowed) {
  return Response.json({ error: 'Rate limit exceeded', code: 'RATE_LIMIT_EXCEEDED' }, { status: 429 });
}
```

## Constraints
- NEVER return raw Redis data without parsing.
- NEVER skip auth on mutating endpoints (POST/PUT/DELETE).
- ALWAYS use try/catch with structured error response.
- ALWAYS log errors to `console.error` with request context.


## Purpose
Standardize all Next.js API routes in AIX Studio with consistent file locations, response shapes (success `{data, meta}` / error `{error, code, details}`), auth patterns, Redis key naming, and rate limiting.

## Constitutional Alignment
Every mutating endpoint (POST/PUT/DELETE) must authenticate via session. Rate limiting prevents resource abuse by any single user. No raw Redis data is ever returned to the client without parsing, preventing internal state leakage.

## Operational Flow
Request arrives → auth check via `getSession()` → rate limit check via `checkRateLimit()` → route handler executes business logic with try/catch → structured JSON response returned — success shape or error shape with appropriate HTTP status code.

## Failure Modes
Skipping auth on mutating endpoints opens security holes; returning unparsed Redis data leaks internal state and serialization details; missing try/catch causes unhandled 500 errors; inconsistent response shapes break client-side type safety.