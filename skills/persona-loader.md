# Skill: Persona Loader

## Purpose

Loads agent personas from the L3 marketplace by ID. Any runtime (IQRA, PiWorker-OS, GemClaw) can call this skill to get a fully-defined persona with role, instructions, tone, constraints, and constitutional alignment. Replaces hardcoded persona definitions in each repo.

## Constitutional Alignment

- **No Duplicates**: One persona definition per ID, shared across the stack.
- **Signed Origin**: Personas loaded through this skill carry an Ed25519 signature, ensuring they come from the sovereign L3 registry.
- **Serve Humanity**: Personas are designed to serve users, not exploit them.

## Operational Flow

1. Agent calls `persona_loader.load(personaId)` with a kebab-case ID.
2. Skill looks up `personas.json` in the L3 marketplace root.
3. Returns the matching persona object: `{ id, name, role, instructions, tone, constraints, specialization }`.
4. Agent injects the persona into its system prompt.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Unknown persona ID | `personas.json` lookup returns null | Return structured error with available IDs |
| Missing personas.json | File not found | Return error: marketplace unavailable |
| Signature invalid | Ed25519 verify fails | Return error: tampered persona definition |
