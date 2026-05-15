# Skill: Self-Improvement Trainer

## Purpose

Analyze past actions and suggest improvements for agent and user workflows. Adapted from GemClaw self-improvement-skills.ts.

## Constitutional Alignment

- **Evolution**: Always seek improvement
- **Honesty**: Admire failures openly, learn from them

## Operational Flow

1. Agent reviews recent actions and outcomes
2. Identifies patterns of success and failure
3. Suggests specific improvements
4. Logs suggestions for future reference

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Insufficient data | < 10 actions | Wait for more data |
| No clear pattern | Analysis fails | Report: no pattern found |
