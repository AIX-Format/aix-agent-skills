# Skill: Calendar Manager

## Purpose

Manage Google Calendar events: create, read, update, delete. Agenda viewing and scheduling.

## Constitutional Alignment

- **Efficiency**: Automate scheduling
- **No Overreach**: Read-only by default

## Operational Flow

1. Agent receives calendar command (agenda, create, search)
2. Authenticates via Google OAuth
3. Calls Calendar API
4. Returns event details

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Conflict | 409 from API | Suggest alternative time |
| Auth expired | 401 | Request re-auth |
