# AIX Skills Gateway (L3 . Phase 6 . x402)

[![AIX Stack](https://img.shields.io/badge/AIX%20STACK-Echo369-39FF14?style=flat-square&labelColor=050505)](https://github.com/Moeabdelaziz007/aix-format/blob/main/AXIOM.md)
[![Spec](https://img.shields.io/badge/SPEC-AIX%2F1.0-39FF14?style=flat-square&labelColor=050505)](https://github.com/Moeabdelaziz007/aix-format/blob/main/AXIOM.md)
[![Layer](https://img.shields.io/badge/LAYER-L3%20%C2%B7%20MARKETPLACE-39FF14?style=flat-square&labelColor=050505)](#)

This subdirectory holds the production gateway that puts the
aix-agent-skills marketplace behind the
[x402 protocol](https://www.x402.org/). A buyer (typically an autonomous
agent in L4/L5/L6) makes an HTTP request for a skill manifest, the
gateway responds with `402 Payment Required` plus an x402 payment
payload, the buyer signs and re-requests with the `X-PAYMENT` header,
the configured facilitator verifies the payment on-chain, and the
gateway streams the manifest back. The whole round trip settles in
about one second on Base.

## Architecture

```
[buyer/agent] --HTTP GET--> [Cloudflare Worker (Hono + x402)] --verify--> [x402 facilitator] --settle--> [Base USDC]
                                          |
                                          +--> stream skill manifest (markdown)
```

The Worker reads `/skills.json` at boot, indexes it in memory, and
exposes the catalogue over six routes:

| Method | Path                              | Payment | Purpose                                |
|--------|-----------------------------------|---------|----------------------------------------|
| GET    | `/`                               | free    | health + version + stack identity      |
| GET    | `/skills`                         | free    | public listing of all skills + prices  |
| GET    | `/skills/:name`                   | free    | public metadata for one skill          |
| GET    | `/skills/:name/manifest`          | x402    | the markdown manifest (paid)           |
| GET    | `/.well-known/skills.json`        | free    | discovery doc for crawler agents       |
| OPTIONS| (cors preflight)                  | free    | universal                              |

Free skills (`price_usdc` is `0` or absent) bypass the payment
middleware entirely; the gateway streams the manifest with no 402
round trip. Paid skills (`price_usdc > 0`) go through the full x402
handshake.

## Local development

```bash
pnpm install              # or npm install
cp .dev.vars.example .dev.vars
# Fill in a TESTNET RECEIVING_WALLET in .dev.vars
pnpm dev                  # binds to 127.0.0.1:8787
```

Smoke-check the public side:

```bash
curl http://127.0.0.1:8787/
curl http://127.0.0.1:8787/skills | jq .total
```

Smoke-check the paid path (requires a buyer wallet on Base Sepolia):

```bash
# First request: expect 402
curl -i http://127.0.0.1:8787/skills/voice-wizard/manifest

# Re-request with an X-PAYMENT header signed by your wallet:
curl -H "X-PAYMENT: <base64-payload>" \
     http://127.0.0.1:8787/skills/voice-wizard/manifest
```

A reference x402 buyer is in `aix-format/scripts/demo_v1_4_payments.js`
and the L4 satellite (`AlphaAxiom`) ships its own buyer in
`money-machine/src-python/` (currently quarantined per the
satellite-trading review policy).

## Configuration

`wrangler.toml` declares three environments:

| Environment   | Network         | Facilitator                              |
|---------------|-----------------|------------------------------------------|
| default (dev) | `base-sepolia`  | `https://x402.org/facilitator`           |
| staging       | `base-sepolia`  | same                                     |
| production    | `base`          | same (Coinbase-hosted)                   |

Secrets are managed via `wrangler secret put`:

```bash
wrangler secret put RECEIVING_WALLET --env production
```

The `NONCE_STORE` KV binding (for anti-replay) is documented in
`wrangler.toml` but disabled in this initial PR; turn it on with
`wrangler kv namespace create NONCE_STORE` when the first paid traffic
arrives and a future commit wires the lookup into the payment
middleware.

## Pricing

Pricing is per-skill via the optional `price_usdc` field on each entry
in `/skills.json` (decimal string). The Phase 6 baseline ships
conservative defaults and explicit prices on a small seed set; refer
to the parent `aix-agent-skills/README.md` for the canonical catalogue.

## Tests

```bash
pnpm test          # vitest, registry-level unit tests
pnpm typecheck     # tsc --noEmit
```

The registry tests pass in plain Node; the Worker-level integration
tests (Miniflare + a mock x402 facilitator) land in a follow-up
because they need a heavier harness.

## Deployment

```bash
wrangler deploy --env production
```

The custom domain `skills.axiomid.app` is declared in `wrangler.toml`;
the L0 root authority delegates that subdomain via the AxiomID DNS
controller. Production deployments require the `RECEIVING_WALLET`
secret to be set in the Cloudflare dashboard.
