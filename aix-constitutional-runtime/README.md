# AIX Constitutional Runtime

Deterministic execution kernel with constitutional governance and append-only trust chain.

## Status

✅ **22/22 E2E tests passing** — zero mocks, real subprocess execution, real crypto hashes.

## Architecture

```
Request → PurityFilter (Constitutional Middleware) → Capability Validator → Runtime Executor → TrustChain Append → Response
```

## Quick Start

```bash
# Run E2E tests (Node.js built-in test runner)
node --test tests/e2e.test.js

# Run standalone demo
node src/runtime/standalone-runtime.js
```

## Files

| File | Purpose |
|---|---|
| `src/skills/purity-filter.ts` | Constitutional middleware — intent analysis, graduated enforcement (allow/warn/escalate/block) |
| `src/skills/trust-chain.ts` | Append-only SHA-256 ledger with integrity verification |
| `src/runtime/standalone-runtime.ts` | Execution kernel — wires filter → chain without Next.js |
| `tests/e2e.test.ts` | E2E suite using Node.js built-in test runner |

## Governance Decisions

| Decision | Score | Execution |
|---|---|---|
| `allow` | ≥ 70 | Execute normally |
| `warn` | 40–69 | Execute with warning logged |
| `escalate` | < 40 | Block, log for human review |
| `block` | 0 (absolute) | Block immediately, no execution |

## Trust Chain Rules

- Append-only (no delete, no modify)
- SHA-256 lineage (prevHash links entries)
- Stores **hashes**, NOT raw payloads (`inputHash`, `outputHash`)
- Integrity verification recomputes all hashes
- "Truth Moment" every 100 entries (auto-verification)
- Tamper detection: broken chain returns `valid: false` + `brokenAt`

## E2E Test Coverage

### Purity Filter (8 tests)
- ✅ Allows clean content (score 100)
- ✅ Blocks haram content: harm, corruption (absolute severity)
- ✅ Blocks empty content
- ✅ Warns on suspicious content (score 65)
- ✅ Escalates high-impact content (score 35)
- ✅ Deterministic (same input → same output)
- ✅ Measures execution time (< 100ms)

### Trust Chain (6 tests)
- ✅ Appends entry with correct lineage (GENESIS → tc-0000)
- ✅ Links entries sequentially (prevHash = previous hash)
- ✅ Verifies integrity of valid chain
- ✅ Detects tampered chain (hash mismatch → brokenAt)
- ✅ Does NOT store raw payloads (only hashes)
- ✅ Generates IDs sequentially (tc-0000, tc-0001, ...)

### Constitutional Runtime (8 tests)
- ✅ Executes clean request end-to-end
- ✅ Blocks haram request BEFORE execution
- ✅ Records passed checks in chain
- ✅ Handles unregistered skill gracefully
- ✅ Handles skill execution errors
- ✅ Maintains chain integrity across mixed requests (passed/blocked/passed/blocked)
- ✅ Supports chain state export/import
- ✅ Performance: 100 entries under 1 second (actual: ~4ms)

## Design Principles

1. **Execution first** — Code runs before it documents itself
2. **Zero mocks** — Tests hit real code paths
3. **Deterministic** — Same input → same output → same hash
4. **Observable** — Every decision is traced and chained
5. **Bounded** — No uncontrolled global state
6. **Graduated enforcement** — Not binary allow/block; 4-tier decision system
