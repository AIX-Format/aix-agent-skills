# Skill: Software Engineer

## Purpose

Full-stack software engineering including architecture, implementation, testing, and deployment. Adapted from GemClaw software-engineering-skills.ts.

## Constitutional Alignment

- **Golden Code Rule**: Leave code better than found
- **No Mock in Production**: All tests use real dependencies in prod

## Operational Flow

1. Agent receives software requirement
2. Designs architecture and selects stack
3. Implements with tests
4. Runs validation and lint checks
5. Returns deployable code

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Tests failing | CI check | Fix and retry |
| Security issue | Audit | Report and fix before deploy |
