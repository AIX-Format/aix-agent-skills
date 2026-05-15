# Skill: Polyglot Coder

## Purpose

Write code across multiple programming languages with best practices. Adapted from GemClaw polyglot-coding-skills.ts.

## Constitutional Alignment

- **Excellence**: Follow language-specific best practices
- **Documentation**: All code must include usage docs

## Operational Flow

1. Agent receives coding task with language
2. Writes clean, idiomatic code following language conventions
3. Includes error handling and input validation
4. Returns code with explanation

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Unsupported language | Check list | Suggest alternatives |
| Syntax errors | Lint check | Fix and retry |
