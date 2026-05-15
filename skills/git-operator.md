# Skill: Git Operator

## Purpose

Performs git operations (commit, push, branch, revert, PR creation) for self-evolving agents across the AIX stack.

## Constitutional Alignment

- **Golden Code Rule**: Leave code better than found
- **Accountability**: All operations logged to TrustChain
- **Safety**: Ref injection prevention on all inputs

## Operational Flow

1. Agent calls git_operator with operation type (commit, push, branch, revert, openPR)
2. Validates all ref tokens via isSafeRefToken()
3. Executes via spawnSync (no shell injection)
4. Returns structured GitRunResult with .ok check
5. Agent verifies result and proceeds

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Unsafe ref token | isSafeRefToken() fails | Reject with structured error |
| Git conflict | Exit code non-zero | Surface conflict details to agent |
| Push rejected | Remote rejects | Pull rebase and retry |
