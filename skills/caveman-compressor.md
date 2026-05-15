# Skill: Caveman Compressor

## Purpose

Compresses LLM prompts by ~60% by removing polite forms, articles, and fluff. Compatible with English and Arabic. Reduces token costs for any agent in the stack.

## Constitutional Alignment

- **No Hallucinations**: Compression is deterministic, not generative
- **Serve Humanity**: Reduces API costs for all agents
- **Efficiency**: Less tokens = faster responses

## Operational Flow

1. Agent sends prompt to Caveman Compressor
2. Skill strips polite forms, articles, and fluff
3. Optionally replaces words with Unicode glyphs (ultra mode)
4. Returns compressed prompt string
5. Agent sends compressed prompt to LLM provider

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Empty input | Null check | Return original empty string |
| Ultra mode fails | Glyph mapping error | Fallback to basic mode |
