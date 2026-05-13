# Rule: Marketplace Skill Quality Gate

**Scope**: `skills/**/*.md`
**Enforced by**: `.github/workflows/skill-quality.yml` and
`scripts/validate_skill_quality.py`.
**Local helper**: `hooks/repo/pre-commit`.

## Why this rule exists

The L3 marketplace catalogs capabilities consumed by sovereign runtimes
(IQRA in particular). A skill that ships with `TODO: Define purpose`
is worse than a missing skill: it claims a capability that does not exist,
poisons downstream discovery, and dilutes trust in the catalog.

At time of writing, 50 of 58 skills in this repo were unfilled stubs.
This rule stops that pattern from continuing.

## What the rule enforces

Every skill file under `skills/` MUST contain real content for the four
required sections defined in `templates/skill-template.md`:

1. Purpose
2. Constitutional Alignment
3. Operational Flow
4. Failure Modes

Section headers may appear in English or in their Arabic equivalents:

| English | Arabic aliases accepted |
|---------|-------------------------|
| Purpose | الغرض, الجوهر |
| Constitutional Alignment | التوافق الدستوري |
| Operational Flow | آليات التشغيل, سير العمل |
| Failure Modes | أنماط الفشل |

A section is considered a stub if its body is empty or matches any of:

- `TODO: Define ...`
- `TBD`
- `<fill in>`
- A single placeholder line followed by the next heading

## Enforcement modes

The validator runs in two modes:

- `--mode=changed` (default in CI): only fail on skills modified in the
  current pull request. Existing stubs are reported but do not block.
  This grandfathers the 50 pre-existing stubs so the gate can land
  without a flag-day rewrite.
- `--mode=strict`: fail on any stub anywhere. Used in the eventual cleanup
  PRs that fill grandfathered stubs.

## How to add a new skill

1. Copy `templates/skill-template.md` to `skills/<snake_case_name>.md`.
2. Replace every placeholder. Do not leave `TODO: Define ...` text.
3. Register the skill in `skills.json` with a real `description`.
4. Run `bash hooks/repo/pre-commit` before pushing to catch issues locally.

## How to fix an existing stub

1. Open the skill file.
2. Fill all four sections with real content.
3. Commit with `feat(skills): fill <skill_name> stub`.
4. The validator now treats the skill as a clean changed file and enforces
   the gate against it.

## Charter alignment

This rule complements `charter.rules.txt`. The charter blocks credential
patterns and surfaces style hints (em-dash, TODO markers); this rule
specifically blocks skill stubs from landing on `main`. The two run as
separate workflows so failures stay attributable.
