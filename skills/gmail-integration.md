# Skill: Gmail Integration

## Purpose

Send, receive, and manage emails through Gmail API with full attachment support. Originally from GemClaw Google Workspace skills.

## Constitutional Alignment

- **Serve Humanity**: Email automation saves time
- **Privacy**: No reading sensitive emails without explicit permission

## Operational Flow

1. Agent receives email command (send, read, search, triage)
2. Authenticates via Google OAuth access token
3. Calls Gmail API endpoint
4. Returns formatted result to agent

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Auth expired | 401 from API | Request re-auth |
| Send failed | API error | Return error details |
