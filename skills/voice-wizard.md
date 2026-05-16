# Skill: Voice Wizard Flow

## What
3-step voice conversation that produces an AIX manifest JSON.
User speaks → AI asks questions → manifest is built turn by turn.

## Architecture
- **STT**: `POST /api/voice-wizard/transcribe` (Groq Whisper)
- **LLM**: `POST /api/voice-wizard/chat` (Gemini Flash)
- **TTS**: `POST /api/voice-wizard/speak` (Edge TTS)
- **Save**: `POST /api/voice-wizard/session` (Redis, TTL 24h)

## Manifest Building Pattern
Each conversation turn extracts ONE field:
- **Turn 1** → `agent.name`
- **Turn 2** → `agent.description`  
- **Turn 3** → `agent.capabilities[]`
- **Turn 4** → `agent.pricing.tier`
- **Turn 5** → `agent.identity.provider`

## The hook (useVoiceWizard.ts) MUST:
- Maintain state: `idle` | `listening` | `processing` | `speaking` | `complete`
- Auto-save to session after every turn
- Emit `onManifestReady(manifest)` when all 5 fields collected

## Constraints
- NEVER call LLM while microphone is open
- NEVER play TTS while recording
- ALWAYS show visual state (pulse = recording, spinner = processing)
- ALWAYS fallback to text input if microphone denied


## Purpose

Orchestrate a 3-step voice conversation flow (STT → LLM → TTS) that builds an AIX agent manifest JSON through multi-turn spoken dialogue. Each turn extracts one manifest field (name, description, capabilities, tier, identity provider) until all 5 fields are collected. Provides the full audio I/O pipeline: transcribes user speech via Groq Whisper, processes via Gemini Flash, responds via Edge TTS, and persists session state to Redis with 24h TTL.

## Constitutional Alignment

- **Microphone Safety**: The LLM is never called while the microphone is open; TTS never plays while recording — prevents audio feedback loops and ensures clean turn boundaries.
- **Visual State Always Visible**: The UI must display the current state (pulse=recording, spinner=processing) — the user is never left guessing if the system is listening.
- **Text Fallback Mandatory**: If microphone permission is denied, the wizard must gracefully fall back to text input — no user is locked out due to hardware constraints.
- **Session Isolation**: Voice sessions are isolated per user (Redis TTL 24h) — no cross-session audio contamination.

## Operational Flow

1. State: `idle` → user triggers the wizard (tap microphone button or say trigger phrase).
2. State: `listening` → microphone opens, audio streams to `POST /api/voice-wizard/transcribe` (Groq Whisper).
3. State: `processing` → transcribed text + current manifest (partial) sent to `POST /api/voice-wizard/chat` (Gemini Flash) → LLM extracts next manifest field or asks clarifying question.
4. State: `speaking` → LLM response sent to `POST /api/voice-wizard/speak` (Edge TTS) → audio played to user.
5. After each turn, session is auto-saved to Redis (`POST /api/voice-wizard/session`).
6. When all 5 manifest fields are collected → emit `onManifestReady(manifest)` and transition to `complete`.
7. If at any turn the LLM determines the field is ambiguous, it asks a follow-up question rather than guessing.

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Microphone permission denied | `getUserMedia` rejects | Fallback to text input mode |
| Groq Whisper times out | STT API > 5s no response | Retry once; if fails again, ask user to type |
| Edge TTS fails | TTS API returns error | Return text-only response, log the TTS error |
| Redis save fails | Session write error | Continue flow in-memory, warn user on next turn |
| LLM produces invalid manifest field | JSON parse fails on response | Re-ask the turn question with more specific prompt |
| Audio feedback (mic picks up speaker) | Energy threshold exceeded during speaking | Mute microphone during TTS playback (NEVER overlap) |