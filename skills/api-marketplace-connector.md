# Skill: API Marketplace Connector

## Purpose

Connect to external API marketplaces (RapidAPI, APILayer) to discover and integrate third-party services. Adapted from GemClaw api-marketplace-skills.ts.

## Constitutional Alignment

- **Security**: Validate all API endpoints before calling
- **No Hardcoded Keys**: Credentials from environment only

## Operational Flow

1. Agent receives service requirement
2. Searches API marketplace for matching APIs
3. Returns available endpoints with pricing
4. Agent selects and integrates

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| No matching API | Empty search | Suggest alternatives |
| API key missing | Env check | Report missing credential |
