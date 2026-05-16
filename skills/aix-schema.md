# Skill: AIX Manifest Schema

## Canonical Location
- **schemas/core/aix.schema.json** (single source of truth)
- **schemas/modules/identity.schema.json**
- **schemas/modules/economics.schema.json**
- **schemas/modules/security.schema.json**

## Required Fields (every valid manifest MUST have)
- `aix_version`: "1.3.0"
- `agent.name`: string (3-50 chars)
- `agent.description`: string (10-200 chars)
- `identity.provider`: "pi-network" | "ethereum" | "solana" | "custom"
- `abom.risk_score`: number (0-100)
- `build_provenance.builder`: string

## Optional but Recommended
- `economics.pricing.tier`: "free" | "builder" | "pro" | "enterprise"
- `abom.saas_services[]`: array
- `skills[]`: array of skill IDs

## Validation Pattern (ALWAYS use in API routes)
```typescript
import { validateManifest } from '@/lib/schema-validator';

const result = validateManifest(manifest);
if (!result.valid) {
  return Response.json({ errors: result.errors }, { status: 400 });
}
```

## Golden Manifests (reference these in tests)
- `tests/golden_manifests/low-risk.aix.json`
- `tests/golden_manifests/sovereign-agent.aix.json`


## Purpose
Define the canonical AIX v1.3.0 manifest schema as the single source of truth for agent identity, economics, security (abom), and build provenance — enforced by a validation pattern used across all API routes.

## Constitutional Alignment
Every manifest must carry an abom.risk_score (0-100) for ethical transparency. Only approved identity providers are permitted. The schema enforces constitutional minima — agent name length, description length, and builder identity are all mandatory fields.

## Operational Flow
Developer creates manifest → validate against `aix.schema.json` via `validateManifest()` → check required fields (aix_version, agent, identity, abom, build_provenance) → append optional fields (economics, skills) → return validated manifest or 400 with error details.

## Failure Modes
Missing required fields returns 400 with validation errors but unclear messages confuse developers; schema version drift between 1.3.0 and future versions causes false negatives; golden manifests not updated alongside schema changes break reference tests.