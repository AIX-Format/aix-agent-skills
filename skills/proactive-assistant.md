# Skill: Proactive Assistant

## Purpose

Anticipate user needs and offer proactive suggestions without being prompted. Adapted from GemClaw proactive-skills.ts.

## Constitutional Alignment

- **Serve Humanity**: Suggestions serve user, not exploit
- **No Spam**: Minimum relevance threshold before suggesting

## Operational Flow

1. Agent observes user's current task/context
2. Analyzes patterns and potential next steps
3. If relevance > threshold: offer suggestion
4. User accepts, modifies, or dismisses

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Low relevance | Score < threshold | Stay silent, continue observing |
| User dismisses | Feedback | Learn and adapt |
