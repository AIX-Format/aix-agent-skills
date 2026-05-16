# Skill: AIX Skills System

## What
Skills are pluggable capabilities attached to agents.
They define WHAT an agent can DO beyond basic chat.

## Skills Registry (static, in /api/skills)
- **web-search**: tier: free
- **code-execution**: tier: builder
- **email-send**: tier: builder
- **voice-response**: tier: pro
- **shopify-connect**: tier: pro
- **abom-scan**: tier: enterprise
- **pi-payment**: tier: pro

## Agent ↔ Skill Relationship (Redis Set)
- **agent:{id}:skills**: Set of skillIds
- **Max skills per agent**: 10 (free=2, builder=5, pro=10, enterprise=unlimited)

## UI Pattern (skills page)
- Grid of skill cards
- Each card: icon + name + tier badge + toggle switch
- Toggle calls `POST`/`DELETE` `/api/agents/{id}/skills`
- Show "Upgrade required" if tier too low

## When Voice Wizard asks about skills
Extract from phrases like:
- "can search the web" → `web-search`
- "can send emails" → `email-send`
- "can run code" → `code-execution`


## Purpose

Static skills registry that maps every agent to its assigned capabilities via a tier-based access model. Defines which skills are available at which tier (free, builder, pro, enterprise), enforces per-agent skill limits, and provides the API contract (Redis-backed agent→skills sets) that the UI and Voice Wizard consume for skill toggling and discovery.

## Constitutional Alignment

- **Tier Integrity**: No agent can access skills from a tier above its subscription — enforced server-side, not just in UI.
- **Max Skills Cap**: Per-tier limits (free=2, builder=5, pro=10, enterprise=unlimited) prevent resource exhaustion.
- **Transparent Tiers**: Every skill card shows its required tier — no hidden paywalls or ambiguous upgrade prompts.
- **Toggle Accountability**: Every skill enable/disable action is logged in the trust chain with agent ID and timestamp.

## Operational Flow

1. Agent is created with a tier and an empty skills set in Redis (`agent:{id}:skills`).
2. UI loads the skills registry from `/api/skills` — renders grid of skill cards with icons, tier badges, and toggle switches.
3. User toggles a skill ON → `POST /api/agents/{id}/skills` with `{ skillId }` → server checks tier eligibility and max skill count → if allowed, adds to Redis set.
4. User toggles skill OFF → `DELETE /api/agents/{id}/skills` with `{ skillId }` → removes from Redis set.
5. Voice Wizard extracts skill intent from user speech (e.g. "can search the web" → maps to `web-search`).
6. Agent runtime reads its skills set before executing any tool call — rejects unassigned skills.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Redis connection lost | `agent:{id}:skills` read fails | Fallback to in-memory cache (stale by max 60s) |
| Agent exceeds max skills | Count check during toggle | Reject toggle, show "upgrade required" message |
| Skill ID does not exist in registry | Lookup returns null | Return 400 with available skill IDs list |
| Tier downgrade leaves agent with too many skills | Tier update hook | Auto-disable skills exceeding new limit, notify user |