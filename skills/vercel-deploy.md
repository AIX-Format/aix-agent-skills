# Skill: Vercel Deployment Fix

## The Problem
Vercel tries to install from wrong path → `ENOENT` error
Command: `npm install --prefix apps/studio`
Error: `/vercel/path0/apps/studio/apps/studio/package.json` not found

## The Fix (do this ONCE)
In Vercel Dashboard → `aix-format-studio` project:
- **Root Directory**: `apps/studio`
- **Install Command**: `npm install`
- **Build Command**: `npm run build`
- **Output Directory**: `.next`

OR create `apps/studio/vercel.json`:
```json
{
  "installCommand": "npm install",
  "buildCommand": "npm run build", 
  "outputDirectory": ".next"
}
```

## ENV Variables Required in Vercel
- `UPSTASH_REDIS_REST_URL`
- `UPSTASH_REDIS_REST_TOKEN`
- `GROQ_API_KEY`
- `GOOGLE_GENERATIVE_AI_API_KEY`
- `NEXT_PUBLIC_PI_APP_ID`
- `STRIPE_SECRET_KEY`
- `NEXTAUTH_SECRET`

## After Deploy Checklist
- [ ] `/api/health` returns `{ status: "ok" }`
- [ ] `/api/registry` returns agents list
- [ ] `/builder` page loads Voice Wizard
- [ ] `/.well-known/agent.aix.json` returns valid JSON


## Purpose

Guide developers through fixing Vercel's `ENOENT` deployment error caused by incorrect root directory configuration. Documents the one-time fix (set root to `apps/studio`, install/build commands at root level), required environment variables, and a post-deploy health checklist to verify the deployment is fully operational.

## Constitutional Alignment

- **Minimal Intervention**: The fix modifies only the Vercel project configuration — no code changes, no monkey-patching, no environment manipulation.
- **Documentation Over Obfuscation**: Every fix step is clearly explained — developers understand why the error occurs rather than blindly following steps.
- **Verification First**: The post-deploy checklist ensures the fix actually worked — no assuming success.
- **Security-Conscious Env Setup**: Environment variables are listed but never contain real values — developers supply their own secrets.

## Operational Flow

1. Developer encounters `ENOENT` error during Vercel deployment with path like `/vercel/path0/apps/studio/apps/studio/package.json`.
2. Open this skill and identify the root cause: Vercel's `--prefix apps/studio` flag causes path doubling when Root Directory is already `apps/studio`.
3. Apply the fix: in Vercel Dashboard → set Root Directory to `apps/studio`, Install Command to `npm install`, Build Command to `npm run build`, Output Directory to `.next`.
4. Alternative: create `apps/studio/vercel.json` with the same commands for version-controlled configuration.
5. Add the 7 required environment variables to the Vercel project.
6. Run the post-deploy checklist: verify `/api/health`, `/api/registry`, `/builder` page, and `/.well-known/agent.aix.json`.
7. If any check fails, inspect the corresponding service log.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Wrong root directory still configured | Path doubling appears in build log | Double-check Vercel Dashboard Root Directory is `apps/studio` (not root `/`) |
| Missing environment variable | API endpoint returns 500 | Check Vercel env vars panel for all 7 required vars |
| `vercel.json` conflicts with Dashboard settings | Dashboard settings override `vercel.json` | Remove Dashboard settings and rely solely on `vercel.json` |
| Next.js config references wrong output path | Build succeeds but 404 on all routes | Ensure `outputDirectory` matches `distDir` in `next.config.js` |