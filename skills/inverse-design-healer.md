# Skill: Inverse Design Healer

## Purpose

Self-healing skill that analyzes failure signatures and proposes deterministic counter-actions (revert, rerun, widen context, or halt). No LLM required — purely deterministic recovery.

## Constitutional Alignment

- **Tawbah**: Self-correction is a core value
- **No Hallucinations**: All counter-actions are deterministic rules
- **Accountability**: All healing events logged to TrustChain

## Operational Flow

1. Agent detects failure with signature (test name, error class, file path, message)
2. Calls inverse-design-healer with the failure signature
3. Skill matches failure against known patterns
4. Returns one of: revert | rerun_with_trace | widen_context | halt
5. Agent executes the recommended action
6. If halt: escalate to human

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Unknown failure | No pattern match | Default: halt and escalate |
| Invalid signature | Schema validation | Return error with format spec |
