/**
 * AIX L3 Skills Gateway . Phase 6 . x402 payment-gated marketplace.
 *
 * Hono application that exposes the aix-agent-skills marketplace over
 * the x402 protocol. Free skills are returned directly; paid skills
 * require an x402 payment header and the buyer is verified against the
 * configured facilitator (Coinbase-hosted by default) before the
 * manifest is streamed back.
 *
 * Routes:
 *   GET  /                          health + version
 *   GET  /skills                    public list of skills + prices
 *   GET  /skills/:name              public metadata for a single skill
 *   GET  /skills/:name/manifest     paid (x402-gated for non-free skills)
 *   GET  /.well-known/skills.json   discovery doc for agents
 */

import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { paymentMiddleware } from 'x402-hono';

import {
  getSkill,
  isPaid,
  listSkills,
  priceFor,
  toPublic,
} from './skills-registry';
import type { Env } from './types';

const app = new Hono<{ Bindings: Env }>();

// CORS is permissive on the read side so agent clients running anywhere
// can discover the catalogue without preflight friction. The actual gate
// is the payment middleware, not CORS.
app.use(
  '*',
  cors({
    origin: '*',
    allowMethods: ['GET', 'POST', 'OPTIONS'],
    allowHeaders: ['Content-Type', 'X-PAYMENT', 'Authorization'],
    exposeHeaders: ['X-PAYMENT-RESPONSE', 'X-AIX-Skill-Name'],
  }),
);

// Health + version: cheap, public, no payment.
app.get('/', (c) => {
  return c.json({
    service: 'aix-skills-gateway',
    version: c.env.GATEWAY_VERSION,
    network: c.env.X402_NETWORK,
    aix: {
      stackVersion: '0.369.0',
      stackCodename: 'Echo369',
      spec: 'AIX/1.0',
      layer: 'L3-gateway',
      authority: 'axiomid.app',
    },
  });
});

// Public catalogue listing. Returns every skill's public projection
// (name, description, tier, price, network, manifest_path) so a buyer
// can pick what they need before they spend anything.
app.get('/skills', (c) => {
  const skills = listSkills().map((s) => toPublic(s, c.env.X402_NETWORK));
  return c.json({
    total: skills.length,
    skills,
  });
});

// Discovery endpoint. Agents that crawl /.well-known/skills.json get a
// stable, machine-friendly index without needing to remember the
// internal URL shape.
app.get('/.well-known/skills.json', (c) => {
  const skills = listSkills().map((s) => toPublic(s, c.env.X402_NETWORK));
  return c.json({
    name: 'aix-agent-skills',
    description: 'AIX L3 marketplace catalogue',
    spec: 'AIX/1.0',
    codename: 'Echo369',
    facilitator: c.env.X402_FACILITATOR_URL,
    skills,
  });
});

// Per-skill public metadata. No payment required because the metadata
// itself is what a buyer needs to decide whether to pay.
app.get('/skills/:name', (c) => {
  const name = c.req.param('name');
  const entry = getSkill(name);
  if (!entry) {
    return c.json({ error: 'skill_not_found', name }, 404);
  }
  return c.json(toPublic(entry, c.env.X402_NETWORK));
});

// Payment middleware: registers per-route prices with the x402 facilitator.
// The middleware short-circuits any GET /skills/:name/manifest call that
// does not carry a valid X-PAYMENT header by returning a 402 with the
// PaymentRequired payload telling the buyer how much, in which token, to
// which wallet, on which network.
app.use('/skills/:name/manifest', async (c, next) => {
  const name = c.req.param('name');
  const entry = getSkill(name);
  if (!entry) {
    return c.json({ error: 'skill_not_found', name }, 404);
  }
  // Free skills bypass the payment middleware entirely.
  if (!isPaid(entry)) {
    return next();
  }
  const price = priceFor(entry);
  const network = entry.network ?? c.env.X402_NETWORK;
  // x402-hono's paymentMiddleware accepts a route -> price map. We
  // construct it dynamically per request because the route is a path
  // parameter.
  const middleware = paymentMiddleware(
    c.env.RECEIVING_WALLET as `0x${string}`,
    {
      [`/skills/${name}/manifest`]: {
        price: `$${price}`,
        network,
        config: {
          description: `AIX skill: ${entry.name} (${entry.tier})`,
          mimeType: 'text/markdown',
        },
      },
    },
    { url: c.env.X402_FACILITATOR_URL },
  );
  return middleware(c, next);
});

// Manifest delivery. After the x402 middleware has verified payment for
// a paid skill (or bypassed for a free one), this handler streams the
// markdown body of the skill back to the buyer.
app.get('/skills/:name/manifest', async (c) => {
  const name = c.req.param('name');
  const entry = getSkill(name);
  if (!entry) {
    return c.json({ error: 'skill_not_found', name }, 404);
  }
  // The manifest body is whatever lives in skills/<name>.md. The Worker
  // bundle embeds these files via a manifest map at build time (see
  // skills-bundle.ts) so the runtime never touches the filesystem.
  const body = await loadManifest(entry.file);
  c.header('X-AIX-Skill-Name', entry.name);
  c.header('X-AIX-Skill-Tier', entry.tier);
  c.header('Content-Type', 'text/markdown; charset=utf-8');
  return c.body(body);
});

// Async manifest loader. Stubbed in the Worker context to fetch from a
// content-addressable origin; the test harness overrides this via a
// module mock so unit tests do not need a network.
async function loadManifest(file: string): Promise<string> {
  // Placeholder . wrangler bundles skills/ via assets binding in a
  // follow-up. For now return a synthetic manifest so the integration
  // test harness can assert end-to-end shape without coupling to the
  // real markdown content.
  return `# ${file}\n\nManifest content placeholder. Replace with skills/ asset binding in deploy hardening.\n`;
}

export default app;
