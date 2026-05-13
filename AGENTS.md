# AGENTS.md — Operating Manual for AI Coding Agents

> 📜 **Stack-wide protocol rules**: read [`AXIOM.md`](https://github.com/Moeabdelaziz007/aix-format/blob/main/AXIOM.md) first. This file complements it with repo-local operating instructions for the AIX Agent Skills marketplace.

## Repository overview

`aix-agent-skills` is the L3 marketplace of the Sovereign Stack: a public catalogue of skills, personas, and runtime adapters consumed by sovereign runtimes (notably IQRA). It hosts:

- `skills/` — markdown skill definitions, snake_case names matching `^[a-z0-9_]+$`.
- `personas/` — versioned agent persona profiles.
- `templates/` — canonical authoring templates. Copy `templates/skill-template.md` when adding a new skill.
- `rules/` — path-scoped quality rules enforced in CI. See `rules/skills.md` for the skill quality gate.
- `hooks/repo/` — optional local git hooks (`pre-commit`) that mirror the CI gates so authors can validate before pushing.
- `aix-constitutional-runtime/` — sample TypeScript runtime that consumes `@axiom/*` packages.
- `go-engine/` — high-performance compute engine for Shannon entropy, topology, and resonance.

## Conventions

- **License**: Apache-2.0.
- **Skill names**: snake_case (`^[a-z0-9_]+$`) per the AIX schema.
- **Branches**: kebab-case (`chore/...`, `feat/...`, `fix/...`).
- **Charter rules**: see `charter.rules.txt`; CI enforces them via `charter-check.yml`.
- **Conventional Commits** preferred for commit subjects.

## What to read before opening a PR

1. [`AXIOM.md`](https://github.com/Moeabdelaziz007/aix-format/blob/main/AXIOM.md) — the supreme constitution.
2. [`charter.rules.txt`](./charter.rules.txt) — repo-local lint rules (AWS keys, em-dash, etc.).
3. [`rules/skills.md`](./rules/skills.md) — the skill quality gate (no stubs may land on `main`).
4. The skill or persona template most similar to what you are adding (`templates/skill-template.md` for skills).

## Sovereign Stack layers

This repo is **L3** in the Sovereign Stack: L1 = `aix-format` (spec), L2 = `iqra` (runtime), L3 = this marketplace. Dependency direction is one-way: L3 depends on L2 depends on L1. No reverse imports.
