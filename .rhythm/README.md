# 🌊 Rhythm Bridge — State Directory

This directory holds the persistent state of the `rhythm-bridge.yml` GitHub
Action that synchronizes the **iqra** Soul OS with the **aix-agent-skills**
marketplace.

## Files

| File | Purpose | Updated by |
|------|---------|-----------|
| `tick_counter` | Monotonic counter incremented every successful run. Drives the modular cadence (which action runs at each tick). | The Action, every cycle. |
| `history.jsonl` | Append-only log of every cycle: tick number, action taken, pairs proposed, pairs merged. Used by the bridge to self-tune. | The Action, every cycle. |

## Cadence

The bridge ticks every 3 hours (aligned with iqra's Pulse369 interval).
Each tick runs an action keyed by its modular position:

| Tick % N | Action |
|---|---|
| Every tick | `TELEMETRY_MIRROR` — sample iqra activity, refresh skill tide states. |
| Every 9 ticks (~daily) | `CROSS_POLLINATE` — match HIGH×ACTIVE skills, open pollination PR. |
| Every 56 ticks (~weekly) | `TIER_REBALANCE` — recompute skill tiers based on accumulated history. |
| Every 392 ticks (~quarterly) | `DEEP_REFORM` — full marketplace re-evaluation. |

## How the bridge measures "tide" without modifying iqra

Since the bridge runs entirely in this repo, it cannot import from iqra at
runtime. Instead, it clones iqra read-only on each tick and uses **proxies**
for the per-skill tide signal:

1. **Mention frequency**: how often each skill name appears in iqra commits
   over the lookback window (default 7 days).
2. **Recency**: weighted decay so recent activity counts more.
3. **File touches**: which files in `iqra/src/lib/iqra/08-skills/` were
   modified, indicating active integration work.

These signals combine into a `tide_score ∈ [0, 1]`. Skills above
`HIGH_THRESHOLD` (0.65 by default) are eligible donors for that cycle.

A skill in the marketplace is "active" if its MD file under `skills/` was
touched in the last 3 hours (the `ACTIVE_WINDOW_HOURS` window).

## Safety

- The bridge never pushes to `main`. It opens PRs on a `tide-sync/*` branch,
  labelled `tide-sync,auto-pollination,needs-tribunal`.
- Same `(donor, recipient)` pair is cooldown-locked for 9 ticks (~27h).
- Hard cap of **7 cross-pollinations per cycle** (the DASTUR seven).
- The pollination patch only **appends** a new `## 🌊 Inherited Patterns`
  section to the recipient MD; it never overwrites existing content.

## Manual trigger

The workflow exposes `workflow_dispatch` so anyone with write access can
trigger a cycle on demand:

```bash
gh workflow run rhythm-bridge.yml -f force_action=CROSS_POLLINATE
```
