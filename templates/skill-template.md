# Skill: <Human Readable Name>

<!--
Canonical template for L3 marketplace skills. Copy this file to
`skills/<snake_case_name>.md` and replace every TODO with real content.

Naming rules (see rules/skills.md):
- Filename: snake_case, matches ^[a-z0-9_]+$
- Title: human readable, may include Arabic
- No em-dash characters (U+2014) anywhere in the file
- Every section below is REQUIRED and must contain real content
- Stubs that still say "TODO: Define ..." will fail CI

Bilingual content is welcome. Section headers may appear in English
(as below) or in Arabic equivalents (see rules/skills.md for the
accepted aliases). The validator accepts either.
-->

## Purpose

What this skill exists to do, in one or two sentences. Avoid abstractions.
Say what a runtime agent gains the moment it calls this skill.

## Constitutional Alignment

How this skill upholds the Sovereign Constitution (see
`personas/0-sovereign/sovereign-constitution.md`). Name the principle,
say how this skill serves it, and call out any tension you accept.

## Operational Flow

The concrete steps the skill takes from input to output. Use a numbered
list. Reference any other skills it composes with by their snake_case name.

1. Step one
2. Step two
3. Step three

## Failure Modes

What goes wrong, how the skill detects it, and how it recovers or escalates.
Cover at minimum: invalid input, dependency unavailable, partial result.

| Mode | Detection | Recovery |
|------|-----------|----------|
| Invalid input | Schema check at entry | Reject with structured error |
| Dependency down | Health probe before call | Fallback or surface to caller |
| Partial result | Output validator | Mark provisional, do not commit |
