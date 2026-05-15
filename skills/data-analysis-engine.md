# Skill: Data Analysis Engine

## Purpose

Perform statistical analysis, data visualization, and predictive modeling. Originally from GemClaw analysis skills.

## Constitutional Alignment

- **Accuracy**: All results must be verifiable
- **No Hallucinations**: Statistical claims need data backing

## Operational Flow

1. Agent sends dataset + analysis request
2. Skill performs statistical computation
3. Generates visualization if requested
4. Returns results + confidence intervals

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Insufficient data | Empty dataset error | Request more data |
| Invalid input | Schema validation | Reject with details |
